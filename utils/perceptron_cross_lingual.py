'''
perform tests on the perceptron model using cross-lingual data
i.e. classifier dutch stress -> tested on german data
'''

from itertools import product
import os
from utils import results
from utils import perceptron

language_names = ['dutch', 'german', 'english', 'polish', 'hungarian']
    

language_pairs = list(product(language_names, repeat = 2))
language_pairs = [x for x in language_pairs if x[0] != x[1]]
all_language_pairs = list(product(language_names, repeat = 2))


def load_classifier(language_name, data_type = 'stress', layer = 'cnn', 
    section = 'vowel', name = '', n = '', random_state = 1):
    clf_filename = perceptron.make_classifier_filename(language_name, data_type,
        layer, section, name, n, random_state)
    clf = perceptron.load_classifier(language_name, data_type, layer, section,
        name, n, random_state)
    return clf, clf_filename

def load_dataset(language_name, data_type, layer, section, name = '', n = ''): 
    dataset_filename = perceptron.make_dataset_filename(language_name, 
        data_type, layer, section, name, n)
    data = perceptron.load_dataset(language_name, data_type, layer, section, 
        name, n)
    return data, dataset_filename

def make_name(other_language):
    return f'other-language-{other_language}'

def make_result_filename(language_name, result_type, layer, section,
    name = '', n = '', random_state = 1):
    f = results.make_result_filename(language_name, result_type, layer, section, 
    name, n, random_state)
    return f
    
def test_classifier_on_other_language(classifier_language_name, 
    test_language_name, data_type = 'stress', layer = 'cnn', section = 'vowel', 
    random_state = 1, overwrite = False, name = '', n = ''):
    name = make_name(test_language_name)
    result_filename = make_result_filename(classifier_language_name,
        data_type, layer, section, name, n, random_state = random_state)
    print(f'testing classifier {classifier_language_name} on',
        f'{test_language_name}')
    print('saving results to', result_filename)
    if os.path.exists(result_filename) and not overwrite:
        print(f'result file {result_filename} exists. skipping')
        return results.Result(result_filename = result_filename)
    clf, clf_filename = load_classifier(classifier_language_name, data_type, 
        layer, section, random_state =  random_state)
    d, d_filename = load_dataset(test_language_name, data_type, layer, section,
         n=n)
    y_test = d['y']
    hyp = clf.predict(d['X'])
    name = make_name(test_language_name)
    result = results.Result(y_test = y_test, hyp = hyp, 
        language_name = classifier_language_name,
        layer = layer, section = section, name = name,  
        random_state = random_state, result_type = data_type,
        dataset_filename = d_filename, 
        classifier_filename = clf_filename, result_filename = result_filename)
    result.save()
    return result

def test_all_language_pairs(overwrite = False):
    output = []
    layers = ['codevector', 5, 11, 17, 23]
    for layer in layers:
        for random_state in range(20):
            for classifier_language_name, test_language_name in language_pairs:
                print(f'testing classifier {classifier_language_name}',
                    f'on {test_language_name}')
                result = test_classifier_on_other_language(
                    classifier_language_name, 
                    test_language_name, layer = layer,
                    random_state = random_state,
                    overwrite = overwrite)
                print(result)
                output.append(result)
    return output


def test_all_mls_language_pairs(overwrite = False):
    output = []
    layers = ['cnn',5,11,17,23]
    for layer in layers:
        for random_state in range(20):
            for classifier_language_name, test_language_name in all_language_pairs:
                print(f'testing classifier {classifier_language_name}',
                    f'on {test_language_name}')
                if test_language_name in ['dutch','hungarian']:
                    continue
                result = test_classifier_on_other_language(
                    classifier_language_name, 
                    test_language_name, layer = layer,
                    random_state = random_state,
                    overwrite = overwrite, n = 'pretrained-xlsr-mls')
                print(result)
                output.append(result)
    return output
