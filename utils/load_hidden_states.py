import numpy as np
from utils import save_hidden_states as shs
from w2v2_hidden_states import frame

hidden_state_indices = 1,3,5,7,9,11,13,15,17,19,21,23,24

def load_word_hidden_states(word):
    return shs.load_word_hidden_states(word)

def phoneme_list_to_combined_hidden_states(phoneme_list, hs = 'cnn',
    mean = False):
    '''load hidden states from list of phonemes'''
    hidden_states_list = []
    for phoneme in phoneme_list:
        if hs == 'cnn':
            hidden_states = phoneme.cnn(mean = False)
        else:
            hidden_states = phoneme.transformer(layer = hs, mean = False)
        if hidden_states is None: continue
        hidden_states_list.append(hidden_states)
    if len(hidden_states_list) == 0: return None
    if len(hidden_states_list) == 1: 
        if mean: return np.mean(hidden_states_list[0], axis = 0)
        return hidden_states_list[0]
    return combine_hidden_states(hidden_states_list, mean = mean)
    

def combine_hidden_states(hidden_states_list, mean = False):
    '''combine hidden states from list of hidden states'''
    combined_hidden_states = np.vstack(hidden_states_list)
    if mean:
        return np.mean(combined_hidden_states, axis = 0)
    return combined_hidden_states


def _replace_none_hidden_states(hidden_states):
    '''some hidden states are None, replace them with correct shaped matrix.
    To slice hidden states, we need to replace None with empty matrices.
    '''
    for i, h in enumerate(hidden_states.hidden_states):
        if h is None:
            hidden_states.hidden_states[i] = np.zeros((0,0,0))

def load_syllable_hidden_states(syllable, word_hidden_states = None):
    '''load syllable hidden states from word hidden states'''
    if not word_hidden_states:
        word_hidden_states = load_word_hidden_states(phoneme.word)
    _replace_none_hidden_states(word_hidden_states)
    start_time = syllable.start_time
    end_time = syllable.end_time
    try:
        o = frame.extract_outputs_times(word_hidden_states,start_time,end_time)
    except IndexError:
        s = syllable
        print(f'syllable {s.ipa} {s.index} to short to extract hidden states')
        return None, word_hidden_states
    o.syllable_identifier = syllable.identifier
    syllable_hidden_states = o
    return syllable_hidden_states

def load_phoneme_hidden_states(phoneme, word_hidden_states = None):
    '''load phoneme hidden states from word hidden states'''
    if not word_hidden_states:
        word = phoneme.word
        if hasattr(word, 'hidden_states'): 
            word_hidden_states = word.hidden_states
        else:
            word_hidden_states = load_word_hidden_states(phoneme.word)
    _replace_none_hidden_states(word_hidden_states)
    start_time = phoneme.start_time
    end_time = phoneme.end_time
    try:
        o = frame.extract_outputs_times(word_hidden_states,start_time,end_time)
    except IndexError:
        p = phoneme
        m = f'phoneme {p.ipa}, index {p.word_index}, to short '
        m += f'(duration: {p.duration:.3f} to extract hidden states'
        return None, word_hidden_states
    o.phoneme_identifier = phoneme.identifier
    o.start_time = start_time
    o.end_time = end_time
    phoneme_hidden_states = o
    return phoneme_hidden_states
        

def add_to_word(word, add_lower = False):
    hs = load_word_hidden_states(word)
    _replace_none_hidden_states(hs)
    word._hidden_states = hs
    if add_lower:
        for s in word.syllables:
            s._hidden_states = load_syllable_hidden_states(s, hs)
        for p in word.phonemes:
            p._hidden_states = load_phoneme_hidden_states(p, hs)
    
