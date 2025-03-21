import glob
from utils import locations
from w2v2_hidden_states import frame
from w2v2_hidden_states import codebook
from w2v2_hidden_states import load
from . import save_codevectors
from . import load_hidden_states as lhs
import numpy as np
from pathlib import Path

def load_codebook(model = None, f = None,checkpoint = None, 
    model_name = None):
    if f is None:
        if model_name == 'pretrained-xlsr':
            f = '../data/codebook_wav2vec2-xls-r-300m.npy'
    elif model_name:
        if not '-cgn' in model_name:
            raise NotImplementedError
        checkpoint = model_name_to_checkpoint(model_name)
    if f and model is None:
        p = Path(f)
        if p.exists(): return np.load(p)
    model = save_codevectors.load_model_pt(checkpoint)
    cb = codebook.load_codebook(model)
    return cb

def load_word_codebook_indices(x, model_name = 'pretrained-xlsr'):
    return save_codevectors.load_word_codebook_indices(x, 
        model_name = model_name)

def load_word_codevectors(x, codebook = None, model_name = 'pretrained-xlsr'):
    if codebook is None: 
        codebook = load_codebook(model_name = model_name)
    ci = load_word_codebook_indices(x, model_name = model_name)
    cv = codebook.multiple_codebook_indices_to_codevectors(ci, codebook)
    return cv

def phoneme_list_to_combined_codevectors(phoneme_list, mean = False):
    '''load codevectors from list of phonemes'''
    return lhs.phoneme_list_to_combined_hidden_states(phoneme_list, 
        hs = 'codevector', mean = mean)

def combine_codevectors(codevectors_list, mean = False):
    '''combine codevectors from list of codevectors'''
    return lhs.combine_hidden_states(codevectors_list, mean = mean)

def load_word_frames(word, word_codebook_indices = None, 
        model_name = 'pretrained-xlsr', codebook = None):
    if not word_codebook_indices:
        word_codebook_indices= load_word_codebook_indices(word, 
            model_name = model_name)
    frames = frame.make_frames(codebook_indices = word_codebook_indices,
        codebook = codebook, start_time = word.start_time)
    return frames

def load_syllable_codevectors(syllable, word_codebook_indices = None, 
    return_codebook_indices = False, model_name = 'pretrained-xlsr',
    codebook = None):
    '''load syllable hidden states from word hidden states'''
    word = syllable.word
    frames = load_word_frames(word, word_codebook_indices, 
        model_name = model_name, codebook = codebook)
    if not frames: return None
    if return_codebook_indices: 
        return frames.codebook_indices(syllable.start_time, syllable.end_time)
    return frames.codevectors(syllable.start_time, syllable.end_time)

def load_phoneme_codevectors(phoneme, word_codebook_indices = None,
    return_codebook_indices = False, model_name = 'pretrained-xlsr',
    codebook = None):
    '''load phoneme hidden states from word hidden states'''
    word = phoneme.word
    frames = load_word_frames(word, word_codebook_indices, model_name,
        codebook = codebook)
    if not frames: return None
    if return_codebook_indices: 
        return frames.codebook_indices(phoneme.start_time, phoneme.end_time)
    return frames.codevectors(phoneme.start_time, phoneme.end_time)



def get_model_checkpoints(language='nl'):
    if language == 'nl':
        dirs = glob.glob(m_nl + '*')
        return [x for x in dirs if not 'last' in x and not 'best' in x]
    if language == 'en':
        dirs = glob.glob(m_en + '*')
        return [x for x in dirs if not 'initialmodel' in x] 
    if language == 'ns':
        dirs = glob.glob(m_ns + '*')
        return [x for x in dirs if not 'initialmodel' in x] 
    return False

def model_checkpoint_to_language(model_checkpoint):
    if 'dutch' in model_checkpoint:
        return 'nl'
    if 'librispeech' in model_checkpoint:
        return 'en'
    if 'audiosetfilter' in model_checkpoint:
        return 'ns'
    return False

def model_checkpoint_to_step(model_checkpoint):
    language = model_checkpoint_to_language(model_checkpoint)
    if language == 'nl':step = model_checkpoint.split('_')[-1]
    else: step = model_checkpoint.split('-')[-1]
    return int(step) 

def language_step_to_checkpoint(language, step):
    checkpoints = get_model_checkpoints(language)
    for checkpoint in checkpoints:
        l = model_checkpoint_to_language(checkpoint)
        s = model_checkpoint_to_step(checkpoint)
        if l == language and s == step:
            return checkpoint
    return None
    
def language_step_to_model_pt(language, step, gpu = False):
    checkpoint = language_step_to_checkpoint(language, step)
    if checkpoint is None:
        return None
    return load.load_model_pt(checkpoint, gpu = gpu)

def language_step_to_model(language, step, gpu = False):
    checkpoint = language_step_to_checkpoint(language, step)
    if checkpoint is None:
        return None
    return load.load_pretrained_model(checkpoint, gpu = gpu)

def language_step_to_model_name(language, step):
    return f'{language}-{step}-cgn'

def model_name_to_checkpoint(model_name):
    language = model_name.split('-')[0]
    step = int(model_name.split('-')[1])
    return language_step_to_checkpoint(language, step)

def model_name_to_model_pt(model_name, gpu = False):
    checkpoint = model_name_to_checkpoint(model_name)
    return load.load_model_pt(checkpoint, gpu = gpu)

def model_name_to_model(model_name, gpu = False):
    checkpoint = model_name_to_checkpoint(model_name)
    return load.load_pretrained_model(checkpoint, gpu = gpu)


base_path = '/vol/mlusers/mbentum/st_phonetics/'
model_path = base_path + 'w2v2_models/'
embed_path = base_path + 'mls_1sp_embed/'
m_nl = model_path + 'wav2vec2_base_dutch_960h/'
m_en = model_path + 'model-wav2vec2_type-base_data-librispeech_version-4/'
m_ns = model_path + 'model-wav2vec2_type-base_data-audiosetfilter_version-2/'

emb_nl = embed_path + 'w2v2-nl/'
emb_en = embed_path + 'w2v2-en/'
emb_ns = embed_path + 'w2v2-ns/'
    
