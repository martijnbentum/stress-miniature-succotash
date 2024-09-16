import pickle
from pathlib import Path
from w2v2_hidden_states import frame
from w2v2_hidden_states import load
from w2v2_hidden_states import to_vector
from utils import locations
from utils import save_hidden_states as shs

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
    
def handle_audio(audio, model = None, gpu = False, save_words = True):
    outputs = audio_to_vector(audio, model, gpu)
    words = audio.word_set.all()
    language_name = audio.language.language
    output = []
    for word in words:
        start_time, end_time, identifier, name = word_to_info(word)
        word_output= frame.extract_outputs_times(outputs, start_time, 
            end_time)
        word_output.identifier = identifier
        word_output.name = name
        if save_words:
            shs.save_word_hidden_states(word, word_output)
        output.append(word_output)
    return output

def word_to_info(word):
    start_time = word.start_time
    end_time = word.end_time
    identifier = word.identifier
    name = word.word
    return start_time, end_time, identifier, name

def audio_filename_to_vector(audio_filename, model = None, gpu = False,
    save_pickle = False):
    if not model: 
        model = load.load_pretrained_model(gpu = gpu)
    outputs = to_vector.filename_to_vector(audio_filename, model = model, 
        gpu = gpu)
    if save_pickle:
        pickle_filename = audio_filename.replace('.wav', '.pickle')
        with open(pickle_filename, 'wb') as fout:
            pickle.dump(outputs)
    return outputs

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
