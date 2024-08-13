from w2v2_hidden_states import frame
from w2v2_hidden_states import codebook
from . import save_codevectors
from . import load_hidden_states as lhs
import numpy as np
from pathlib import Path

def load_codebook(model = None, f ='../data/codebook_wav2vec2-xls-r-300m.npy'):
    if model is None:
        p = Path(f)
        if p.exists(): return np.load(p)
    model = save_codevectors.load_model_pt()
    cb = codebook.load_codebook(model)
    return cb

cb = load_codebook()

def load_word_codebook_indices(x):
    return save_codevectors.load_word_codebook_indices(x)

def load_word_codevectors(x, _codebook = None):
    if _codebook is None: _codebook = cb
    ci = load_word_codebook_indices(x)
    cv = codebook.multiple_codebook_indices_to_codevectors(ci, _codebook)
    return cv

def phoneme_list_to_combined_codevectors(phoneme_list, mean = False):
    '''load codevectors from list of phonemes'''
    return lhs.phoneme_list_to_combined_hidden_states(phoneme_list, 
        hs = 'codevector', mean = mean)

def combine_codevectors(codevectors_list, mean = False):
    '''combine codevectors from list of codevectors'''
    return lhs.combine_hidden_states(codevectors_list, mean = mean)

def load_word_frames(word, word_codebook_indices = None):
    if not word_codebook_indices:
        word_codebook_indices= load_word_codebook_indices(word)
    frames = frame.make_frames(codebook_indices = word_codebook_indices,
        codebook = cb, start_time = word.start_time)
    return frames

def load_syllable_codevectors(syllable, word_codebook_indices = None, 
    return_codebook_indices = False):
    '''load syllable hidden states from word hidden states'''
    word = syllable.word
    frames = load_word_frames(word, word_codebook_indices)
    if not frames: return None
    if return_codebook_indices: 
        return frames.codebook_indices(syllable.start_time, syllable.end_time)
    return frames.codevectors(syllable.start_time, syllable.end_time)

def load_phoneme_codevectors(phoneme, word_codebook_indices = None,
    return_codebook_indices = False):
    '''load phoneme hidden states from word hidden states'''
    word = phoneme.word
    frames = load_word_frames(word, word_codebook_indices)
    if return_codebook_indices: 
        return frames.codebook_indices(phoneme.start_time, phoneme.end_time)
    return frames.codevectors(phoneme.start_time, phoneme.end_time)
    

    
