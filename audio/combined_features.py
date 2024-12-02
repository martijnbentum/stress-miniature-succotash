from audio import pitch
from audio import formants
import json
import numpy as np
import os
import pickle
from progressbar import progressbar
from sklearn.metrics import classification_report
from sklearn.metrics import matthews_corrcoef
from utils import lda, perceptron
from utils import density_classifier
from utils import select
from utils import locations
    


def get_f0_f1_f2(phoneme):
    f0 = pitch._to_pitch(phoneme.f0)
    f1f2 = formants._to_f1f2(phoneme.f1, phoneme.f2)
    if not f1f2: f1, f2 = None, None
    else: f1, f2 = f1f2
    return [f0, f1, f2]

def get_combined_features(phoneme):
    features = get_f0_f1_f2(phoneme)
    spectral_tilt = phoneme.spectral_tilt 
    if not spectral_tilt: spectral_tilt = [None, None, None, None]
    features.extend(spectral_tilt)
    features.append( phoneme.intensity )
    features.append( phoneme.duration)
    return features

def make_dataset(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''
    make dataset of all stress features per phoneme for an LDA classifier.
    '''
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    X, y = [], []
    for stress_status,vowels in d.items():
        y_value = 1 if stress_status == 'stress' else 0
        for vowel in vowels:
            line = get_combined_features(vowel)
            if None in line: continue
            X.append(line) 
            y.append(y_value)
    return X, y

def make_dataset_filename(language_name):
    language_name = language_name.lower()
    dataset_dir= locations.dataset_dir
    dataset_filename = f'{dataset_dir}/xy_dataset-stress_'
    dataset_filename += f'language-{language_name}_section-vowel_'
    dataset_filename += f'layer-combined-features_n-_name-.pickle'
    return dataset_filename

def save_dataset(language_name, X, y):
    dataset_filename = make_dataset_filename(language_name)
    print(f'saving combined features dataset to {dataset_filename}')
    d = {'X':X,'y':y, 'language_name':language_name, 
        'layer':'combined-features','n':None, 'name':None, 'section':'vowel'}
    with open(dataset_filename, 'wb') as f:
        pickle.dump(d, f)

def load_dataset(language_name):
    dataset_filename = make_dataset_filename(language_name)
    print(f'loading combined features dataset from {dataset_filename}')
    if not os.path.exists(dataset_filename):
        print(f'file {dataset_filename} does not exist')
        return None
    with open(dataset_filename, 'rb') as f:
        d = pickle.load(f)
    return d['X'], d['y']

def train_lda(X, y, test_size = .33, report = True,random_state = 42):
    '''
    train LDA classifier on the combined features dataset
    '''
    y_test, hyp, clf = lda.train_lda(X, y, test_size = test_size, 
        report = report, random_state = random_state)
    return y_test, hyp, clf


def train_perceptron(X,y, random_state = 42, max_iter = 3000):
    '''
    train perceptron classifier on the combined features dataset
    '''
    y_test, hyp, clf = perceptron.train_mlp_classifier(X,y, 
        random_state = random_state, max_iter = max_iter)
    return y_test, hyp, clf

def plot_lda_hist(X, y, clf = None, new_figure = True, 
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = 'combined', xlim = None, 
    plot_density = False):
    '''plot distribution of LDA scores for stress and no stress vowels'''
    if not clf:
        clf, _, _ = train_lda(X, y, report = False)
    lda.plot_lda_hist(X, y, clf, new_figure = new_figure, 
        minimal_frame = minimal_frame, ylim = ylim, add_left = add_left,
        add_legend = add_legend, bins = bins, xlabel = xlabel, xlim = xlim,
        plot_density = plot_density)
    return clf

    
