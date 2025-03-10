import os
import pickle
from pathlib import Path
from progressbar import progressbar
from w2v2_hidden_states import frame
from w2v2_hidden_states import load
from w2v2_hidden_states import to_vector
from utils import locations
from utils import save_hidden_states as shs
from utils import st_phonetic_map_cnn_to_ci as sc
import torch
import gc

def load_model(gpu = False):
    '''load the pretrained wav2vec2 model'''
    return load.load_pretrained_model(gpu = gpu)

def audio_to_vector(audio, model = None, gpu = False):
    if not model: 
        model = load.load_pretrained_model(gpu = gpu)
    audio_filename = audio.filename
    outputs = to_vector.filename_to_vector(audio_filename, model = model, 
        gpu = gpu)
    return outputs

def check_any_bi_syllabic_words(words):
    for word in words:
        if word.n_syllables == 2:
            return True
    return False
    
def handle_audio(audio, model = None, gpu = False, save_words = True, 
    model_name = 'pretrained-xlsr',
    only_bisyllabic_words = False, remove_layer_list = None):
    words = audio.word_set.all()
    if only_bisyllabic_words and not check_any_bi_syllabic_words(words):
        return []
    outputs = audio_to_vector(audio, model, gpu)
    language_name = audio.language.language
    output = []
    for word in words:
        if only_bisyllabic_words and word.n_syllables != 2:
            continue
        start_time, end_time, identifier, name = word_to_info(word)
        word_output= frame.extract_outputs_times(outputs, start_time, 
            end_time)
        word_output.identifier = identifier
        word_output.name = name
        if save_words:
            shs.save_word_hidden_states(word, word_output, 
                model_name = model_name, remove_layer_list = remove_layer_list)
        output.append(word_output)
    del outputs
    gc.collect()
    torch.cuda.empty_cache()
    return output

def handle_mls_audio(audio, model = None, gpu = False, save_words = True,
    model_name = 'pretrained-xlsr', 
    only_bisyllabic_words = False):
    model_name += '-mls'
    print('handling', audio, 'with model_name', model_name)
    print('only_bisyllabic_words', only_bisyllabic_words)
    return handle_audio(audio, model, gpu, save_words, model_name, 
        only_bisyllabic_words)

def handle_cgn_audio(audio, model = None, gpu = False, save_words = True,
    model_name = 'pretrained-xlsr', 
    only_bisyllabic_words = False, remove_layer_list = None):
    model_name += '-cgn'
    print('handling', audio, 'with model_name', model_name)
    print('only_bisyllabic_words', only_bisyllabic_words)
    return handle_audio(audio, model, gpu, save_words, model_name, 
        only_bisyllabic_words, remove_layer_list)

def handle_st_phonetics_language(audios, language = 'nl', gpu = False, 
    save_words = True, only_bisyllabic_words = False,
    remove_layer_list = [0,2,4,6,8,10], steps = None):
    if not steps: steps = sc.steps
    o =sc.link_models_and_embeds(language)
    mf = [sc.step_to_model(s,linked_models_and_embeds = o) for s in steps]
    for m in mf:
        model_checkpoint = m['model']
        name = f'{m["language"]}-{m["step"]}'
        print('handling', name, 'with model_checkpoint', model_checkpoint)
        model = load.load_pretrained_model(model_checkpoint, gpu = gpu)
        index = 0
        n_audios = len(audios)
        for audio in progressbar(audios):
            o = handle_cgn_audio(audio, model, gpu, save_words, name, 
                only_bisyllabic_words, remove_layer_list)
            del o 
            gc.collect()
            torch.cuda.empty_cache()
        del model
        gc.collect()
        torch.cuda.empty_cache()
    
    

def word_to_info(word):
    start_time = word.start_time
    end_time = word.end_time
    identifier = word.identifier
    name = word.word
    return start_time, end_time, identifier, name

def audio_filename_to_vector(audio_filename, model = None, gpu = False,
    save_pickle = False, output_filename = ''):
    if save_pickle and not output_filename:
        audio_filename = str(audio_filename)
        output_filename = audio_filename.replace('.wav', '.pickle')
        if os.path.exists(output_filename):
            print('skipping', output_filename, 'already exists')
            return False
    if not model: 
        model = load.load_pretrained_model(gpu = gpu)
    outputs = to_vector.filename_to_vector(audio_filename, model = model, 
        gpu = gpu)
    if save_pickle:
        print('saving', output_filename)
        with open(output_filename, 'wb') as fout:
            pickle.dump(outputs, fout)
    return outputs

def directory_to_vectors(directory, model, gpu = False, output_directory = ''):
    p = Path(directory)
    output = []
    print('processing', directory, 'and saving to', output_directory)
    for audio_filename in progressbar(p.glob('*.wav')):
        print('processing', audio_filename)
        f = str(audio_filename)
        pickle_filename = f.replace('.wav', '.pickle')
        if output_directory:
            if not output_directory.endswith('/'):
                output_directory += '/'
            pickle_filename = pickle_filename.replace(directory, 
                output_directory)
        if Path(pickle_filename).exists():
            print('skipping', pickle_filename, 'already exists')
            continue
        o = audio_filename_to_vector(f, model, gpu, save_pickle = True, 
            output_filename = pickle_filename)
        output.append(o)
    return output

'''
no speed up
def audio_to_hidden_states(audio, model = False, gpu = False):
    outputs = audio_to_vector(audio, model, gpu)
    language_name = audio.language.language
    hdf5_filename = shs.language_name_to_hdf5_filename(language_name)
    name = audio.identifier
    if shs.check_hidden_states_exists(hdf5_filename,name): return False
    shs.save_hidden_states(hdf5_filename,name,outputs)
    return True
'''
