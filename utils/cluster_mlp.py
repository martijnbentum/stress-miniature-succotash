from datasets import acoustic_correlates
import numpy as np
import random
from text.models import Word, Dataset, Language
from utils import perceptron
from utils import select
from utils import tsne

languages = ['dutch', 'english', 'german', 'polish','hungarian']
random.seed(42)

def get_vowel_stress_dict(language_name = 'dutch'):
    return acoustic_correlates.get_vowel_stress_dict(language_name)

def sample_vowels(vsd, n = 1000):
    stress = random.sample(vsd['stress'], n)
    no_stress = random.sample(vsd['no_stress'], n)
    return stress, no_stress

def vowel_to_x_y(vowel, layer = 17):
    x = vowel.transformer(layer, mean = True)
    y = vowel.stress
    return x, y


def load_xy_data(language_name, layer = 17):
    data = perceptron.load_dataset(language_name, 'stress', layer,'vowel')
    return data

def sample_data(X, n = 1000):
    n_items = len(X)
    indices = random.sample(range(n_items), n)
    print('indices', len(indices), n_items, n)
    X_sample = X[indices,:]
    return X_sample

def sample_stress_no_stress(language_name = '', data = None, n = 1000, 
    layer = 17):
    if not language_name and data is None:
        raise ValueError('need either language_name or data')
    if data is None:data = load_xy_data(language_name, layer)
    X, y = data['X'], data['y']
    stress = X[np.where(y == 1),:][0]
    stress = sample_data(stress, n)
    no_stress = X[np.where(y == 0),:][0]
    no_stress = sample_data(no_stress, n)
    return stress, no_stress


def make_dataset(n = 1000, layer = 17):
    d = {}
    for language_name in languages:
        print(f'processing {language_name}')
        stress, no_stress = sample_stress_no_stress(language_name)
        sn, sns = len(stress), len(no_stress)
        assert sn == sns
        X = np.vstack((stress, no_stress))
        y = [f'{language_name} stress'] * sn
        y += [f'{language_name} no stress'] * sn
        d[language_name] = {'X': X, 'y': y}
    for i, language_name in enumerate(languages):
        if i == 0:
            X = d[language_name]['X']
            y = d[language_name]['y']
        else:
            X = np.vstack((X, d[language_name]['X']))
            y += d[language_name]['y']
    return d, X, y


def get_activations(clf, X):
    #WIP!
        hidden_layer_sizes = clf.hidden_layer_sizes
        if not hasattr(hidden_layer_sizes, "__iter__"):
            hidden_layer_sizes = [hidden_layer_sizes]
        hidden_layer_sizes = list(hidden_layer_sizes)
        layer_units = [1] + hidden_layer_sizes + \
            [clf.n_outputs_]
        activations = [X]
        for i in range(clf.n_layers_ - 1):
            activations.append(np.empty((X.shape[0],
                                         layer_units[i + 1])))
        clf._forward_pass(activations)
        return activations, layer_units

