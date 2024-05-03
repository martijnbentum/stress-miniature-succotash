import pickle
from w2v2_hidden_states import frame
from w2v2_hidden_states import load
from w2v2_hidden_states import to_vector

def load_model(gpu = False):
    return load.load_pretrained_model(gpu = gpu)

def audio_to_vector(audio, model = None, gpu = False):
    if not model: 
        model = load.load_pretrained_model(gpu = gpu)
    audio_filename = audio.filename
    outputs = to_vector.filename_to_vector(audio_filename, model = model, 
        gpu = gpu)
    return outputs

def handle_audio(audio, model = None, gpu = False, save_words = True,
    output_directory = None):
    if not output_directory:
        output_directory = load.hidden_state_directory
    outputs = audio_to_vector(audio, model, gpu)
    words = audio.word_set.all()
    output = []
    for word in words:
        start_time, end_time, identifier, name = word_to_info(word)
        word_output= frame.extract_outputs_times(outputs, start_time, 
            end_time)
        word_output.identifier = identifier
        word_output.name = name
        if save_words:
            filename = output_directory + identifier + ".pickle"
            pickle.dump(word_output,open(filename, "wb"))
        output.append(word_output)
    return output

def word_to_info(word):
    start_time = word.start_time
    end_time = word.end_time
    identifier = word.identifier
    name = word.word
    return start_time, end_time, identifier, name
