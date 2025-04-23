from . import link_audio_to_model
from w2v2_hidden_states import codebook, load
from utils import save_codevectors 
from progressbar import progressbar
from . import select_materials
from . import model_names
from . import step_list
from . import model_checkpoints 


def get_checkpoints(language = 'nl'):
    return model_checkpoints.get_model_checkpoints(language)
    

def language_step_to_model_checkpoint(language, step):
    return model_checkpoints.language_step_model_checkpoint(language, step)

def language_step_to_model_pt(language, step, gpu = False):
    checkpoint = language_step_to_model_checkpoint(language, step)
    if checkpoint is None:
        return None
    return load.load_model_pt(checkpoint, gpu = gpu)

def language_step_to_codebook(language, step, gpu = False):
    model_pt = language_step_to_model_pt(language, step, gpu = gpu)
    return codebook.load_codebook(model_pt)

def language_codebooks(language, gpu = False):
    steps = step_list.steps
    d = {}
    for step in steps:
        codebook = language_step_to_codebook(language, step, gpu = gpu)
        d[step] = codebook
    return d


def language_step_to_model_name(language, step):
    return f'{language}-{step}-cgn'

def save_word_codevectors(word, model_pt, model_name, overwrite = False):
    save_codevectors.save_word_codebook_indices(word, model_pt, model_name,
        overwrite = overwrite)

def handle_all_languages(words = None, overwrite = False):
    if words is None:
        words = select_materials.load_words()
    for language in ['nl', 'en', 'ns']:
        print(f'language: {language}')
        handle_language(language, words)

def handle_language(language = 'nl', words = None, overwrite = False, 
    steps = None):
    if words is None:
        words = select_materials.load_words()
    if steps is None:
        steps = model_names.steps
    for step in steps:
        checkpoint = language_step_to_model_checkpoint(language, step)
        print(f'checkpoint: {checkpoint}')
        handle_checkpoint(checkpoint, words, overwrite = overwrite)

def handle_checkpoint(checkpoint, words = None, overwrite = False):
    if words is None:
        words = select_materials.load_words()
    language = model_checkpoints.model_checkpoint_to_language(checkpoint)
    step = model_checkpoints.model_checkpoint_to_step(checkpoint)
    model_name = language_step_to_model_name(language, step)
    model_pt = load.load_model_pt(checkpoint, gpu = False)
    for word in progressbar(words):
        save_word_codevectors(word, model_pt, model_name, overwrite = overwrite)
