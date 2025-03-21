import h5py
import json
from utils import locations
import numpy as np
import pickle
from pathlib import Path
import random
from . import save_hidden_states as shs
from . import load_hidden_states as lhs
from w2v2_hidden_states import codebook
from w2v2_hidden_states import load

def load_codebook_indices(hdf5_filename, name):
    '''
    hdf5_filename   filename for the hdf5 data storage file
    name            name for the data in the hdf5 storage 
    '''
    if not check_codebook_indices_exists(hdf5_filename, name):
        return None
    with h5py.File(hdf5_filename, 'r') as fin:
        pickled_array = fin[name][:]
    codebook_indices = shs.pickled_array_to_data(pickled_array)
    return codebook_indices

def save_codebook_indices(hdf5_filename, name, codebook_indices):
    '''
    hdf5_filename   filename for the hdf5 data storage file
    name            name for the data in the hdf5 storage 
    codebook_indices output from neural network
    '''
    pickled_array = shs.data_to_pickled_array(codebook_indices)
    with h5py.File(hdf5_filename, 'a') as fout:
        fout.create_dataset(name, data = pickled_array)

def check_codebook_indices_exists(hdf5_filename, name):
    if not Path(hdf5_filename).exists(): return False
    with h5py.File(hdf5_filename, 'r') as fin:
        exists = name in fin.keys()
    return exists

def check_word_codebook_indices_exists(word):
    hdf5_filename = shs.word_to_hdf5_filename(word)
    name = make_codebook_indices_name(word)
    return check_codebook_indices_exists(hdf5_filename, name)

def remove_codebook_indices(hdf5_filename, name):
    if not Path(hdf5_filename): return False
    with h5py.File(hdf5_filename, 'a') as fout:
        exists = name in fout.keys()
        if exists:
            del fout[name]
    removed = exists
    return removed

def remove_word_codebook_indices(word):
    hdf5_filename = shs.word_to_hdf5_filename(word)
    name = make_codebook_indices_name(word)
    if not check_codebook_indices_exists(hdf5_filename, name):
        print(f'word codebook_indices does not exist, skipping {word}')
    remove_codebook_indices(hdf5_filename, name)

def load_word_codebook_indices(word, model_name = 'pretrained-xlsr'):
    '''load hidden states for a specific word.'''
    hdf5_filename = shs.word_to_hdf5_filename(word, 
        model_name = model_name)
    name = make_codebook_indices_name(word)
    ci = load_codebook_indices(hdf5_filename, name)
    return ci

def _word_to_codebook_indices(word, model_pt, model_name = 'pretrained-xlsr'):
    outputs = lhs.load_word_hidden_states(word, model_name = model_name)
    if outputs is None: return None
    codebook_indices = codebook.outputs_to_codebook_indices(outputs, model_pt)
    return codebook_indices

def save_word_codebook_indices(word, model_pt, model_name = 'pretrained-xlsr'):
    '''save hidden states for a specific word.'''
    filename = shs.word_to_hdf5_filename(word, model_name = model_name)
    name = make_codebook_indices_name(word)
    if check_codebook_indices_exists(filename, name):
        print('word codebook_indices already saved, skipping')
        return
    codebook_indices = _word_to_codebook_indices(word, model_pt, 
        model_name = model_name)
    if codebook_indices is None: 
        print(f'codebook indices not found, skipping {word}')
        return
    save_codebook_indices(filename, name, codebook_indices)

def make_codebook_indices_name(word):
    return word.identifier + '_codebook_indices'

def load_model_pt(checkpoint = None):
    '''load the pretrained wav2vec2 model with the codebook'''
    # return codebook.load_model_pt()
    return load.load_model_pt(checkpoint = checkpoint)

