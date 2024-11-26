from audio import pitch
from audio import formants
import json
import numpy as np
from progressbar import progressbar
from utils import lda
from utils import density_classifier
from utils import select


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

def train_lda(X, y, test_size = .33, report = True,random_state = 42):
    '''
    train LDA classifier on the combined features dataset
    '''
    clf, data, report = lda.train_lda(X, y, test_size = test_size, 
        report = report, random_state = random_state)
    return clf, data, report

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

    
