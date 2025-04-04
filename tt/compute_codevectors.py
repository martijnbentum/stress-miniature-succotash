from . import link_audio_to_model
from w2v2_hidden_states import codebook, load
from utils import save_codevectors 
from progressbar import progressbar
from . import select_materials
from . import model_names


def get_checkpoints():
    checkpoints = link_audio_to_model.get_model_folders()
    return checkpoints

def language_step_to_checkpoint(language, step):
    checkpoints = get_checkpoints()
    for checkpoint in checkpoints:
        l = link_audio_to_model.dir_to_language(checkpoint)
        if l not in ['nl', 'en', 'ns']:
            continue
        s = link_audio_to_model.dir_to_step(checkpoint)
        if l == language and s == step:
            return checkpoint
    return None

def language_step_to_model_pt(language, step, gpu = False):
    checkpoint = language_step_to_checkpoint(language, step)
    if checkpoint is None:
        return None
    return load.load_model_pt(checkpoint, gpu = gpu)

def language_step_to_model_name(language, step):
    return f'{language}-{step}-cgn'

def save_word_codevectors(word, model_pt, model_name):
    save_codevectors.save_word_codebook_indices(word, model_pt, model_name)

def handle_all_languages(words = None):
    if words is None:
        words = select_materials.load_words()
    for language in ['nl', 'en', 'ns']:
        print(f'language: {language}')
        handle_language(language, words)

def handle_language(language = 'nl', words = None):
    if words is None:
        words = select_materials.load_words()
    steps = model_names.steps
    for step in steps:
        checkpoint = language_step_to_checkpoint(language, step)
        print(f'checkpoint: {checkpoint}')
        handle_checkpoint(checkpoint, words)

def handle_checkpoint(checkpoint, words = None):
    if words is None:
        words = select_materials.load_words()
    language = link_audio_to_model.dir_to_language(checkpoint)
    step = link_audio_to_model.dir_to_step(checkpoint)
    model_name = language_step_to_model_name(language, step)
    model_pt = language_step_to_model_pt(language, step)
    for word in progressbar(words):
        save_word_codevectors(word, model_pt, model_name)
