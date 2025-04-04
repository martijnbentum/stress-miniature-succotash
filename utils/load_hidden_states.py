import numpy as np
from utils import save_hidden_states as shs
from w2v2_hidden_states import frame

hidden_state_indices = 1,3,5,7,9,11,13,15,17,19,21,23,24

def check_model_name_linked_to_audio(audio, model_name):
    '''check if the model name is linked to the audio'''
    hidden_state_model = audio.hidden_state_model
    model_names = [x.split('_')[-1] for x in hidden_state_model.split(',')]
    return model_name in model_names 
    

def load_word_hidden_state_frames(word, model_name = 'pretrained-xlsr'):
    if not check_model_name_linked_to_audio(word.audio, model_name):
        print(f'word {word.identifier} not linked to model {model_name}')
        return None
    frames = shs.load_word_hidden_state_frames(word, model_name = model_name)
    return frames

def frames_to_cnn(frames, start_time = None, end_time = None, mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert frames to cnn hidden states'''
    cnn = frames.cnn(start_time = start_time, end_time = end_time,
        percentage_overlap = percentage_overlap, middle_frame = middle_frame,
        average = mean)
    return cnn

def frames_to_transformer(frames, layer, start_time = None, end_time = None,
    mean = False, percentage_overlap = None, middle_frame = False):
    '''convert frames to transformer hidden states'''
    transformer = frames.transformer(layer, start_time = start_time,
        end_time = end_time, average = mean, 
        percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return transformer

def phoneme_to_cnn(phoneme, word_hidden_state_frames = None,
    model_name = 'pretrained-xlsr', mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert phoneme to cnn hidden states'''
    if word_hidden_state_frames is None:
        word_hidden_state_frames = load_word_hidden_state_frames(phoneme.word, 
            model_name = model_name)
    if word_hidden_state_frames is None: return None
    frames = word_hidden_state_frames
    cnn = frames_to_cnn(frames, start_time = phoneme.start_time,
        end_time = phoneme.end_time, mean = mean,
        percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return cnn
    
def phoneme_to_transformer(phoneme, layer, word_hidden_state_frames = None,
    model_name = 'pretrained-xlsr', mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert phoneme to transformer hidden states'''
    if word_hidden_state_frames is None:
        word_hidden_state_frames = load_word_hidden_state_frames(phoneme.word, 
            model_name = model_name)
    if word_hidden_state_frames is None: return None
    frames = word_hidden_state_frames
    transformer = frames_to_transformer(frames, layer,
        start_time = phoneme.start_time, end_time = phoneme.end_time,
        mean = mean, percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return transformer
    
def syllable_to_cnn(syllable, word_hidden_state_frames = None,
    model_name = 'pretrained-xlsr', mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert syllable to cnn hidden states'''
    if word_hidden_state_frames is None:
        word_hidden_state_frames = load_word_hidden_state_frames(syllable.word, 
            model_name = model_name)
    if word_hidden_state_frames is None: return None
    frames = word_hidden_state_frames
    cnn = frames_to_cnn(frames, start_time = syllable.start_time,
        end_time = syllable.end_time, mean = mean,
        percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return cnn

def syllable_to_transformer(syllable, layer, word_hidden_state_frames = None,
    model_name = 'pretrained-xlsr', mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert syllable to transformer hidden states'''
    if word_hidden_state_frames is None:
        word_hidden_state_frames = load_word_hidden_state_frames(syllable.word, 
            model_name = model_name)
    if word_hidden_state_frames is None: return None
    frames = word_hidden_state_frames
    transformer = frames_to_transformer(frames, layer,
        start_time = syllable.start_time, end_time = syllable.end_time,
        mean = mean, percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return transformer

def word_to_cnn(word, model_name = 'pretrained-xlsr', mean = False,
    percentage_overlap = None, middle_frame = False):
    '''convert word to cnn hidden states'''
    frames = load_word_hidden_state_frames(word, model_name = model_name)
    if frames is None: return None
    cnn = frames_to_cnn(frames, mean = mean, start_time = word.start_time,
        end_time = word.end_time, percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return cnn
    
def word_to_transformer(word, layer, model_name = 'pretrained-xlsr', 
    mean = False, percentage_overlap = None, middle_frame = False):
    '''convert word to transformer hidden states'''
    frames = load_word_hidden_state_frames(word, model_name = model_name)
    if frames is None: return None
    transformer = frames_to_transformer(frames, layer, 
        start_time = word.start_time, end_time = word.end_time,
        mean = mean, percentage_overlap = percentage_overlap,
        middle_frame = middle_frame)
    return transformer

    

def load_syllable_hidden_states(syllable, word_hidden_states = None, 
    model_name = 'pretrained-xlsr', percentage_overlap = None,
    middle_frame = False):
    '''load syllable hidden states from word hidden states'''
    if word_hidden_states is None:
        word_hidden_states = load_word_hidden_states(syllable.word,
            model_name = model_name)
    
    _replace_none_hidden_states(word_hidden_states)
    start_time = syllable.start_time
    end_time = syllable.end_time
    try:
        o = frame.extract_outputs_times(word_hidden_states,start_time,end_time,
            percentage_overlap = percentage_overlap)
    except IndexError:
        s = syllable
        print(f'syllable {s.ipa} {s.index} to short to extract hidden states')
        return None, word_hidden_states
    o.syllable_identifier = syllable.identifier
    syllable_hidden_states = o
    return syllable_hidden_states

def load_phoneme_hidden_states(phoneme, word_hidden_states = None, 
    model_name = 'pretrained-xlsr', percentage_overlap = None):
    '''load phoneme hidden states from word hidden states'''
    if not word_hidden_states:
        word = phoneme.word
        word_hidden_states = load_word_hidden_states(word, 
            model_name = model_name)
    if not word_hidden_states: return None
    _replace_none_hidden_states(word_hidden_states)
    start_time = phoneme.start_time
    end_time = phoneme.end_time
    try:
        o = frame.extract_outputs_times(word_hidden_states,start_time,end_time,
            percentage_overlap = percentage_overlap)
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
        

def add_to_word(word, add_lower = False, model_name = 'pretrained-xlsr'):
    hs = load_word_hidden_states(word, model_name = model_name)
    if not hs is None: 
        _replace_none_hidden_states(hs)
    word._hidden_states = hs
    if add_lower:
        for s in word.syllables:
            if hs is None: s._hidden_states = None
            else: s._hidden_states = load_syllable_hidden_states(s, hs)
        for p in word.phonemes:
            if hs is None: p._hidden_states = None
            else: p._hidden_states = load_phoneme_hidden_states(p, hs)


def load_layers_from_hidden_states(hidden_states, layers, mean = False):
    output = {}
    if hidden_states is None: return None
    if 'codevector' in layers:
        raise ValueError('codevector not part of hidden states object')
    for layer in layers:
        if type(layer) == int:
            o = hidden_states.hidden_states[layer]
        elif layer == 'cnn':
            o = hidden_states.extract_features
        else: raise ValueError(f'layer {layer} not recognized')
        if o.size == 0: 
            raise ValueError(f'layer {layer} is empty')
        if mean: o = np.mean(o, axis = 0)
        output[layer] = o
    return output

def load_layers_from_multiple_hidden_states(hidden_states_list, layers, 
    mean = False):
    output = {}
    for hs in hidden_states_list:
        if hs is None: return None
    if 'codevector' in layers:
        raise ValueError('codevector not part of hidden states object')
    for layer in layers:
        if type(layer) == int:
            o = np.vstack([hs.hidden_states[layer] for hs in 
                hidden_states_list])
        elif layer == 'cnn':
            o = np.vstack([hs.extract_features for hs in 
                hidden_states_list])
        else: raise ValueError(f'layer {layer} not recognized')
        if o.size == 0: 
            raise ValueError(f'layer {layer} is empty')
        o = o[0]
        if mean: o = np.mean(o, axis = 0)
        output[layer] = o
    return output

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


def phoneme_list_to_combined_hidden_states(phoneme_list, hs = 'cnn',
    mean = False, model_name = 'pretrained-xlsr'):
    '''load hidden states from list of phonemes'''
    hidden_states_list = []
    for phoneme in phoneme_list:
        if hs == 'cnn':
            hidden_states = phoneme.cnn(mean = False, model_name = model_name)
        elif hs == 'codevector':
            hidden_states = phoneme.codevector(mean = False)
        elif hs == 'hidden_states':
            hidden_states = phoneme.hidden_states(model_name = model_name)
        else:
            hidden_states = phoneme.transformer(layer = hs, mean = False,
                model_name = model_name)
        if hidden_states is None: continue
        hidden_states_list.append(hidden_states)
    if len(hidden_states_list) == 0: return None
    if len(hidden_states_list) == 1: 
        if mean: return np.mean(hidden_states_list[0], axis = 0)
        return hidden_states_list[0]
    return combine_hidden_states(hidden_states_list, mean = mean)
    
