import h5py
from utils import locations
import numpy as np
import pickle
from pathlib import Path


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
    if language_name: 
        hdf5_filename = language_name_to_hdf5_filename(language_name)
    else: hdf5_filename = word_to_hdf5_filename(word)
    name = word.identifier
    hidden_states = load_hidden_states(hdf5_filename, name)
    return hidden_states

def save_word_hidden_states(word, hidden_states, language_name = None):
    '''save hidden states for a specific word.'''
    if language_name: 
        hdf5_filename = language_name_to_hdf5_filename(language_name)
    else: hdf5_filename = word_to_hdf5_filename(word)
    name = word.identifier
    save_hidden_states(hdf5_filename, name, hidden_states)

def check_word_hidden_states_exists(word, language_name = None):
    if language_name: 
        hdf5_filename = language_name_to_hdf5_filename(language_name)
    else: hdf5_filename = word_to_hdf5_filename(word)
    name = word.identifier
    exists = check_hidden_states_exists(hdf5_filename, name)
    return exists

def remove_word_hidden_states(word, language_name = None):
    if language_name: 
        hdf5_filename = language_name_to_hdf5_filename(language_name)
    else: hdf5_filename = word_to_hdf5_filename(word)
    name = word.identifier
    removed = remove_hidden_states(hdf5_filename, name)
    return removed
    
    

def language_name_to_hdf5_filename(language_name):
    filename = 'hidden_states_' + language_name + '.h5'
    filename = locations.hidden_states_dir / filename
    return filename

def audio_to_hdf5_filename(audio):
    filename = language_to_hdf5_filename(audio.language)
    return filename

def word_to_hdf5_filename(word):        
    filename = language_to_hdf5_filename(word.language)
    return filename

def syllable_to_hdf5_filename(syllable):
    filename = word_to_hdf5_filename(syllable.word)
    return filename

def phoneme_to_hdf5_filename(phoneme):
    filename = word_to_hdf5_filename(phoneme.word)
    return filename

def language_to_hdf5_filename(language):
    language_name = language.language.lower()
    filename = language_name_to_hdf5_filename(language_name)
    return filename


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
