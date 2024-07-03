import h5py
import json
from utils import locations
import numpy as np
import pickle
from pathlib import Path
import random

n_hdf5_files = 500

def remove_last_hidden_state(hidden_states):
    hidden_states.last_hidden_state = None
    hidden_states['last_hidden_state'] = None

def remove_layers(hidden_states, layers = [0,2,4,6,8,10,12,14,16,18,20,22]):
    for layer_index in layers:
        hidden_states.hidden_states[layer_index] = None
        hidden_states['hidden_states'][layer_index] = None

def load_hidden_states(hdf5_filename, name):
    '''
    hdf5_filename   filename for the hdf5 data storage file
    name            name for the data in the hdf5 storage 
    '''
    with h5py.File(hdf5_filename, 'r') as fin:
        pickled_array = fin[name][:]
    hidden_states = pickled_array_to_data(pickled_array)
    return hidden_states

def save_hidden_states(hdf5_filename, name, hidden_states):
    '''
    hdf5_filename   filename for the hdf5 data storage file
    name            name for the data in the hdf5 storage 
    hidden_states   output from neural network
    '''
    pickled_array = data_to_pickled_array(hidden_states)
    with h5py.File(hdf5_filename, 'a') as fout:
        fout.create_dataset(name, data = pickled_array)

def check_hidden_states_exists(hdf5_filename, name):
    if not Path(hdf5_filename).exists(): return False
    with h5py.File(hdf5_filename, 'r') as fin:
        exists = name in fin.keys()
    return exists

def remove_hidden_states(hdf5_filename, name):
    if not Path(hdf5_filename): return False
    with h5py.File(hdf5_filename, 'a') as fout:
        exists = name in fout.keys()
        if exists:
            del fout[name]
    removed = exists
    return removed

def data_to_pickled_array(data):
    '''prepare hidden states data to be stored in hdf5 file
    '''
    pickled_data = pickle.dumps(data)
    pickled_array = np.frombuffer(pickled_data, dtype = 'S1')
    return pickled_array

def pickled_array_to_data(pickled_array):
    '''unpack pickled data.'''
    pickled_data = pickled_array.tobytes()
    data = pickle.loads(pickled_data)
    return data


def load_word_hidden_states(word, language_name = None):
    '''load hidden states for a specific word.'''
    hdf5_filename = word_to_hdf5_filename(word)
    name = word.identifier
    hidden_states = load_hidden_states(hdf5_filename, name)
    return hidden_states

def _save_hidden_state_number(audio,number):
    audio.hidden_state = number
    audio.save()

def save_word_hidden_states(word, hidden_states, language_name = None):
    '''save hidden states for a specific word.'''
    filename = word_to_hdf5_filename(word, language_name)
    name = word.identifier
    if check_word_hidden_states_exists(word, filename):
        print('word hidden states already saved, skipping')
        return
    remove_last_hidden_state(hidden_states)
    remove_layers(hidden_states)
    save_hidden_states(filename, name, hidden_states)

def check_word_hidden_states_exists(word, filename = None):
    if not filename:
        filename = word_to_hdf5_filename(word)
    name = word.identifier
    exists = check_hidden_states_exists(filename, name)
    return exists

def hdf5_filename(language_name, number):
    language_name = language_name.lower()
    filename = 'hidden_states_' + language_name + '_' + str(number) + '.h5'
    filename = locations.hidden_states_dir / filename
    return filename

def language_to_language_name(language):
    return language.language.lower()

def audio_to_hdf5_filename(audio, language_name = None):
    if not language_name:
        language_name = language_to_language_name(audio.language)
    number = audio.hidden_state
    if not number: 
        filename, number = get_hdf5_filename(language_name)
        _save_hidden_state_number(audio, number)
    filename = hdf5_filename(language_name, number)
    return filename

def word_to_hdf5_filename(word, language_name = None):
    filename = audio_to_hdf5_filename(word.audio, language_name)
    return filename

def syllable_to_hdf5_filename(syllable):
    filename = word_to_hdf5_filename(syllable.word)
    return filename

def phoneme_to_hdf5_filename(phoneme):
    filename = word_to_hdf5_filename(phoneme.word)
    return filename


def hdf5_keys(filename):
    with h5py.File(filename, 'r') as fin:
        keys = list(fin.keys())
    return keys



# batch loading is a little bit faster than per word loading
    
def batch_load_word_hidden_states(words, language_name = None):
    if language_name: 
        hdf5_filename = language_name_to_hdf5_filename(language_name)
    else: hdf5_filename = word_to_hdf5_filename(words[0])
    names = [word.identifier for word in words]
    output = batch_load_hidden_states(hdf5_filename, names)
    return output

def batch_load_hidden_states(hdf5_filename, names):
    output = {}
    with h5py.File(hdf5_filename, 'r') as fin:
        for name in names:
            pickled_array = fin[name][:]
            hidden_states = pickled_array_to_data(pickled_array)
            output[name] = hidden_states
    return hidden_states


#split hdf5 files
def filenames_to_numbers(filenames):
    numbers = []
    for filename in filenames:
        number = filename_to_number(filename)
        if number: numbers.append(number)
    return numbers

def filename_to_number(filename):
    number = str(filename).split('_')[-1].split('.h5')[0]
    try: number = int(number)
    except ValueError:
        print(number, filename,'could not convert')
        return None
    return number

def find_filename_with_number(number, filenames = [], language_name = ''):
    if not filenames and not language_name: return None
    if language_name and not filenames:
        filenames = find_filenames_with_language_name(language_name)
    for filename in filenames:
        n = filename_to_number(filename)
        if n == number: return filename
    return None

def find_filenames_with_language_name(language_name):
    pattern = 'hidden_states_'+language_name+'*.h5'
    fn = list(locations.hidden_states_dir.glob(pattern))
    return fn

def find_filename_with_space(filenames):
    for filename in filenames:
        if has_space(filename): return filename

def has_space(filename, max_n_items = 1000):
    if not filename: return False
    k = hdf5_keys(filename)
    return len(k) <= max_n_items

def get_hdf5_filename(language_name, current_number = None, max_n_items = 1000):
    filenames = find_filenames_with_language_name(language_name)
    if current_number:
        filename = find_filename_with_number(current_number, 
            filenames = filenames, language_name = language_name)
        if has_space(filename): return filename, number
    numbers = filenames_to_numbers(filenames)
    number = max(numbers) + 1 if numbers else 1
    return hdf5_filename(language_name, number), number
        
    

