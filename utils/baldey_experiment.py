# see ldrepo make_baldey_selection.py for creation of dataset and annotations

# experiment to test stress classifier performance on words and non words
# from the baldey dataset


from w2v2_hidden_states import frame
import pickle
from pathlib import Path
import numpy as np
import json
from sklearn.metrics import matthews_corrcoef, accuracy_score
from sklearn.metrics import classification_report

baldey_directory = Path('../baldey_annotate/')
recording_directory = baldey_directory / 'recordings'
classifier_directory = baldey_directory / 'classifiers'
dataset_directory = baldey_directory / 'datasets'

def layerwise_correct_words_non_words(model = 'pre-trained', 
    layers = ['cnn', 5, 11, 17, 23]):
    '''create output of correct words and non words per layer'''
    for layer in layers:
        words, non_words = split_word_non_words(layer, model = model)
        correct, total, percentage = vowel_infos_to_correct_count(words)
        print('words',layer, percentage)
        correct, total, percentage = vowel_infos_to_correct_count(non_words)
        print('non words',layer, percentage)

def vowel_infos_to_correct_count(vowel_infos):
    '''count correct predictions in vowel_infos'''
    correct = 0
    for vowel_info in vowel_infos:
        if vowel_info['correct']:
            correct += 1
    return correct, len(vowel_infos), round(correct / len(vowel_infos) * 100,2)

def split_word_non_words(layer = 'cnn', model = 'pre-trained'):
    '''split vowel_infos in words and non words'''
    vowel_infos = load_vowel_infos(layer, model = model)
    word_vowels = []
    non_word_vowels = []
    for vowel_info in vowel_infos:
        if vowel_info['is_a_word']:
            word_vowels.append(vowel_info)
        else:
            non_word_vowels.append(vowel_info)
    return word_vowels, non_word_vowels

def load_hypothesis(layer = 'cnn', model = 'pre-trained'):
    '''load stress status predictions for a model layer'''
    f = dataset_directory / model / f'prediction_{layer}.npy'
    return np.load(f)

def make_predictions(layer = 'cnn', save = False, model = 'pre-trained'):
    '''make stress status predictions for a model layer'''
    clf = load_classifier(layer, model = model)
    gt = load_or_make_ground_truth()
    x = load_x(layer, model = model)
    hyp = clf.predict(x)
    f = dataset_directory / model / f'prediction_{layer}.npy'
    np.save(f, hyp)
    print(layer)
    print('matthews', matthews_corrcoef(gt, hyp))
    print('accuracy', accuracy_score(gt, hyp))
    print(classification_report(gt, hyp))
    return hyp
    
def make_predictions_all_layers(model = 'pre-trained', 
    layers = ['cnn', 5, 11, 17, 23]):
    '''make predictions for all specified layers of a model.
    model: 'pre-trained' or 'fine-tuned'
    layers: list of layers to make predictions for
    '''
    for layer in layers:
        make_predictions(layer, save = True, model = model)

def load_classifier(layer = 'cnn', model = 'pre-trained'):
    '''load stress classifier for a model layer
    layer: 'cnn' or int (for transformer layer)
    model: 'pre-trained' or 'fine-tuned' 
    '''
    if model == 'pre-trained':
        name = f'clf_dutch_stress_{layer}_vowel___9.pickle'
    else:
        name = f'clf_dutch_stress_{layer}_vowel__{model}_9.pickle'
    f = classifier_directory / model / name
    print('laoding', f)
    with open(f, 'rb') as fin:
        clf = pickle.load(fin)
    return clf

def get_pickle_filenames(model = 'pre-trained'):
    '''get all filenames for hidden states pickle files for a model'''
    directory = recording_directory / model
    return list(directory.glob('*.pickle'))

def load_pickle_file(filename):
    '''load hidden states from a pickle file'''
    with open(filename,'rb') as fin:
        hidden_states = pickle.load(fin)
    return hidden_states

def cnn(hidden_states, mean = True):
    '''extract cnn features from hidden states object
    compute mean if mean is True, mean is over the time dimension
    '''
    cnn_features = hidden_states.extract_features[0]
    if mean: return np.mean(cnn_features, axis = 0)
    return cnn_features

def transformer(hidden_states, layer = 1, mean = True):
    '''extract transformer features from hidden states object
    layer: int, layer number of the transformer
    mean: bool, mean is over the time dimension
    '''
    transformer_features = hidden_states.hidden_states[layer][0]
    if mean: return np.mean(transformer_features, axis = 0)
    return transformer_features

def word_to_hidden_states(word, model = 'pre-trained'):
    pickle_filenames = get_pickle_filenames(model)
    for filename in pickle_filenames:
        if word == filename.stem:
            return load_pickle_file(filename)
    raise ValueError(f'no hidden states found for {word}')

def word_to_word_info(word, dataset_info = None):
    if dataset_info is None: dataset_info = load_dataset_info()
    for info in dataset_info:
        if word == info[0]:
            return info
    raise ValueError(f'no info found for {word}')

def vowel_to_x(layer, hidden_states, vowel_info, syllable_number, 
    stressed_syllable_number, word):
    ipa, start_time, end_time = vowel_info.split(',')
    start_time = float(start_time)
    end_time = float(end_time)
    vowel_info = {'ipa':ipa, 'start':start_time, 'end':end_time,
        'syllable_number':syllable_number, 
        'stressed_syllable_number': stressed_syllable_number, 'word':word}
    o = frame.extract_outputs_times(hidden_states,start_time,end_time)
    if layer == 'cnn': x = cnn(o)
    else: x = transformer(o, layer)
    vowel_info['x'] = x
    return vowel_info

def word_to_x(layer, word_info, model = 'pre-trained'):
    '''load embeddings for the vowels (corresponding to syllables) in a word.
    '''
    word = word_info[0]
    hidden_states = word_to_hidden_states(word, model = model)
    annotation = word_to_annotation(word)
    vowel1 = vowel_to_x(layer, hidden_states, word_info[-2], 1, annotation, 
        word_info)
    vowel2 = vowel_to_x(layer, hidden_states, word_info[-1], 2, annotation, 
        word_info)
    return [vowel1, vowel2]

def layer_to_x(layer, save_vowel_infos = False, save_x = False, 
    model = 'pre-trained'):
    '''load embeddings for all items (ie vowels) in the dataset 
    for a model layer
    layer: 'cnn' or int (for transformer layer)
    save_vowel_infos: bool, save vowel_infos to json
    save_x: bool, save x to numpy array
    model: 'pre-trained' or 'fine-tuned'
    '''
    word_list = load_or_make_word_list()
    dataset_info = load_dataset_info()
    x = []
    vowel_infos = []
    for i,word in enumerate(word_list):
        word_info = word_to_word_info(word, dataset_info)
        vowel1, vowel2 = word_to_x(layer, word_info, model = model)
        for vowel in [vowel1, vowel2]:
            x.append(vowel['x'])
            del vowel['x']
            vowel['word_index'] = i
            vowel_infos.append(vowel)
    x = np.array(x)
    if save_vowel_infos:
        f = dataset_directory / model / f'vowel_infos_{layer}.json'
        with open(f, 'w') as fout:
            json.dump(vowel_infos, fout)
    if save_x:
        f = dataset_directory / model / f'x_{layer}.npy'
        np.save(f, x)
    return x, vowel_infos

def load_vowel_infos(layer = 'cnn', add_predictions = True, 
    model = 'pre-trained'):
    '''load vowel information with prediction (hyp) for a model layer
    layer: 'cnn' or int (for transformer layer)
    add_predictions: bool, add classifier predictions to vowel_infos
    model: 'pre-trained' or 'fine-tuned'
    '''
    f = dataset_directory / model / f'vowel_infos_{layer}.json'
    with open(f, 'r') as fin:
        vowel_infos = json.load(fin)
    if add_predictions:
        hyp = load_hypothesis(layer, model = model)
        for i,vowel_info in enumerate(vowel_infos):
            stress = int(vowel_info['stressed_syllable_number'] ==
                vowel_info['syllable_number'])
            is_a_word = vowel_info['word'][2] == 'word'
            vowel_info['is_a_word'] = is_a_word
            vowel_info['ground_truth'] = stress
            vowel_info['prediction'] = hyp[i]
            vowel_info['correct'] = stress == hyp[i]
    return vowel_infos

def layers_to_x(model = 'pre-trained', layers = ['cnn', 5, 11, 17, 23]):
    '''load embeddings for all items (ie vowels) in the dataset
    for all layers of a model
    model: 'pre-trained' or 'fine-tuned'
    layers: list of model layers to process
    '''
    print('handling model', model, 'layers', layers)
    for layer in layers:
        print('processing', layer)
        layer_to_x(layer, save_vowel_infos = True, save_x = True,model = model)

def load_x(layer = 'cnn', model = 'pre-trained'):
    '''load embeddings for all items (ie vowels) in the dataset 
    for a model layer
    '''
    f = dataset_directory / model / f'x_{layer}.npy'
    print('loading', f)
    return np.load(f)

def word_to_annotation(word, annotations = None):
    '''get stress annotation for a word'''
    if annotations is None: annotations = load_annotations()
    for annotation in annotations:
        if word == annotation[1]:
            return annotation[-1]
    raise ValueError(f'no annotation found for {word}')

def load_or_make_ground_truth():
    '''load or make ground truth for the baldey dataset
    indicating the stress status of the vowels in the dataset
    '''
    f = dataset_directory / 'ground_truth.npy'
    if f.exists():return np.load(f)
    output = []
    with open(dataset_directory / 'vowel_infos_cnn.json', 'r') as fin:
        vowel_infos = json.load(fin)
    for vowel_info in vowel_infos:
        stressed = int(vowel_info['stressed_syllable_number'] == 
            vowel_info['syllable_number'])
        output.append(stressed)
    output = np.array(output)
    with open(f, 'w') as fout:
        np.save(f, output)
    return output

def load_dataset_info():
    '''load information about the words in the baldey dataset'''
    f = baldey_directory / 'baldey_syl-2_word-combined_vowels.txt'
    with open(f, 'r') as fin:
        dataset_info = [line.split('\t') for line in fin.read().split('\n')]
    return dataset_info
    
def load_annotations(annotator = 'martijn'):
    '''load stress annotations for a specific annotator of the words in the
    baldey dataset.
    '''
    f = baldey_directory / f'{annotator}_annotations.json'
    with open(f, 'r') as fin:
        annotations = json.load(fin)
    return annotations

def load_or_make_word_list():
    '''load or make a list of words in the baldey dataset'''
    f = baldey_directory / 'word_list.txt'
    if f.exists():
        with open(f, 'r') as fin:
            word_list = fin.read().split('\n')
        return word_list
    word_list = []
    for filename in get_pickle_filenames('pre-trained'):
        word = filename.stem
        word_list.append(word)
    with open(f, 'w') as fout:
        fout.write('\n'.join(word_list))
    return word_list
