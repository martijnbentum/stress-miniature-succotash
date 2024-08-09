import h5py
import json
from utils import locations
import numpy as np
import pickle
from pathlib import Path
import random
from . import save_hidden_states as shs

def load_codebook_indices(hdf5_filename, name):
    '''
    hdf5_filename   filename for the hdf5 data storage file
    name            name for the data in the hdf5 storage 
    '''
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

def remove_codebook_indices(hdf5_filename, name):
    if not Path(hdf5_filename): return False
    with h5py.File(hdf5_filename, 'a') as fout:
        exists = name in fout.keys()
        if exists:
            del fout[name]
    removed = exists
    return removed

def load_word_codebook_indices(word):
    '''load hidden states for a specific word.'''
    hdf5_filename = shs.word_to_hdf5_filename(word)
    name = make_codebook_indices_name(word)
    ci = load_codebook_indices(hdf5_filename, name)
    return ci

def save_word_codebook_indices(word, codebook_indices, language_name = None):
    '''save hidden states for a specific word.'''
    filename = shs.word_to_hdf5_filename(word, language_name)
    name = make_codebook_indices_name(word)
    if check_codebook_indices_exists(filename, name):
        print('word codebook_indices already saved, skipping')
        return
    save_codebook_indices(filename, name, codebook_indices)

def make_codebook_indices_name(word):
    return word.identifier + '_codebook_indices'


