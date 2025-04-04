import h5py
import json
from utils import locations
import numpy as np
import pickle
from pathlib import Path
from progressbar import progressbar
import random
from w2v2_hidden_states import frame

n_hdf5_files = 500

def _migrate_audio_hidden_state_to_hidde_state_model(audios):
    for audio in progressbar(audios):
        audio.hidden_state_model = f'{audio.hidden_state}_pretrained-xlsr'
        audio.save()

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
    if not check_hidden_states_exists(hdf5_filename, name): return None
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


def load_word_hidden_state_frames(word, model_name = 'pretrained-xlsr'):
    '''load hidden states for a specific word.'''
    hdf5_filename = word_to_hdf5_filename(word, model_name = model_name)
    name = word.identifier
    hidden_states = load_hidden_states(hdf5_filename, name)
    frames = frame.make_frames(hidden_states, start_time = word.start_time)
    return frames

def audio_hidden_state_model_field_to_dict(hidden_state_model):
    if not hidden_state_model: return {}
    model_saves = hidden_state_model.split(',')
    model_dict = {}
    for model_save in model_saves:
        number, name = model_save.split('_')
        model_dict[name] = int(number)
    return model_dict

def hidden_state_model_field_dict_to_string(model_dict):
    model_saves = [f'{number}_{name}' for name,number in model_dict.items()]
    model_saves = ','.join(model_saves)
    return model_saves

def check_model_name(model_name):
    if '_' in model_name:
        raise ValueError('model_name cannot contain underscore', model_name)

def _save_hidden_state_number(audio,number, model_name = 'pretrained-xlsr'):
    check_model_name(model_name)
    d = audio_hidden_state_model_field_to_dict(audio.hidden_state_model)
    if model_name in d:
        print(f'{audio.identifier} overwriting {model_name} in {d[model_name]}',
            f'with {number}')
        d[model_name] = number
    else: 
        print(f'{audio.identifier} adding {model_name} with {number}')
        d[model_name] = number
    audio.hidden_state_model = hidden_state_model_field_dict_to_string(d)
    audio.save()

def save_word_hidden_states(word, hidden_states, language_name = None, 
    model_name = 'pretrained-xlsr', remove_layer_list = None):
    '''save hidden states for a specific word.'''
    check_model_name(model_name)
    filename = word_to_hdf5_filename(word, language_name, model_name)
    name = word.identifier
    if check_word_hidden_states_exists(word, filename):
        print('word hidden states already saved, skipping')
        return
    remove_last_hidden_state(hidden_states)
    if remove_last_hidden_state is None:
        remove_layers(hidden_states)
    else: 
        remove_layers(hidden_states, layers = remove_layer_list)
    save_hidden_states(filename, name, hidden_states)

def check_word_hidden_states_exists(word, filename = None):
    if not filename:
        filename = word_to_hdf5_filename(word)
    name = word.identifier
    exists = check_hidden_states_exists(filename, name)
    return exists

def hdf5_filename(language_name, number, model_name = 'pretrained-xlsr'):
    language_name = language_name.lower()
    filename = 'hidden_states_' + language_name + '_' + str(number) + '.h5'
    directory = locations.hidden_states_dir / model_name 
    if not directory.exists():
        print('creating directory', directory)
        directory.mkdir()
    filename = locations.hidden_states_dir / model_name / filename
    return filename

def language_to_language_name(language):
    return language.language.lower()

def _audio_to_number(audio, model_name = 'pretrained-xlsr'):
    check_model_name(model_name)
    if not audio.hidden_state_model:
        return None
    d = audio_hidden_state_model_field_to_dict(audio.hidden_state_model)
    if model_name in d:
        return d[model_name]
    return None

def audio_to_hdf5_filename(audio, language_name = None, 
    model_name = 'pretrained-xlsr'):
    check_model_name(model_name)
    if not language_name:
        language_name = language_to_language_name(audio.language)
    number = _audio_to_number(audio, model_name)
    if not number: 
        filename, number = get_hdf5_filename(language_name, 
            model_name = model_name)
        _save_hidden_state_number(audio, number, model_name = model_name)
    filename = hdf5_filename(language_name, number, model_name)
    return filename

def word_to_hdf5_filename(word, language_name = None, 
    model_name = 'pretrained-xlsr'):
    check_model_name(model_name)
    filename = audio_to_hdf5_filename(word.audio, language_name, 
        model_name = model_name)
    return filename

def syllable_to_hdf5_filename(syllable, model_name = 'pretrained-xlsr'):
    filename = word_to_hdf5_filename(syllable.word, model_name = model_name)
    return filename

def phoneme_to_hdf5_filename(phoneme, model_name = 'pretrained-xlsr'):
    filename = word_to_hdf5_filename(phoneme.word, model_name = model_name)
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

def find_filenames_with_language_name(language_name, 
    model_name = 'pretrained-xlsr'):
    pattern = 'hidden_states_'+language_name+'*.h5'
    directory = locations.hidden_states_dir / model_name
    fn = list(directory.glob(pattern))
    return fn

def has_space(filename, max_n_items = 1000):
    if not filename: return False
    k = hdf5_keys(filename)
    return len(k) <= max_n_items

def get_hdf5_filename(language_name, current_number = None, max_n_items = 1000,
    model_name = 'pretrained-xlsr'):
    filenames = find_filenames_with_language_name(language_name, model_name)
    numbers = filenames_to_numbers(filenames)
    if not current_number:
        if numbers: current_number = max(numbers)
        else: current_number = 0
    filename = find_filename_with_number(current_number, 
        filenames = filenames, language_name = language_name)
    if has_space(filename): return filename, current_number
    number = max(numbers) + 1 if numbers else 1
    return hdf5_filename(language_name, number, model_name), number
        
    

