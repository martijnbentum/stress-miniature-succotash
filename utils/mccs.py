from audio import duration
from audio import formants
from audio import intensity
from audio import pitch
from audio import combined_features
import json
import numpy as np
from progressbar import progressbar
from utils import density_classifier
from utils import lda

def handle_language(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    mccs = compute_mccs_with_ci(n = 100, vowel_stress_dict = d, 
        name = language_name)
    return mccs
    
def compute_mccs_with_ci(n = 100, formant_data = None, intensities = None,
    pitch = None, durations = None, spectral_tilts = None, 
    combined_feature = None,vowel_stress_dict = None, name = '', save = True):
    mccs = {'formant':[], 'intensity':[], 'pitch':[], 'duration':[],
        'spectral tilt','combined features':[]}
    for key in mccs.keys():
        if key == 'formant':
            data = formant_data
            function = make_formant_classifier
        if key == 'intensity':
            data = intensities
            function = make_intensity_classifier
        if key == 'pitch':
            data = pitch
            function = make_pitch_classifier
        if key == 'duration':
            data = durations
            function = make_duration_classifier
        if key == 'spectral tilt':
            data = spectral_tilts
            function = make_spectral_tilt_classifier
        if key == 'combined features':
            data = combined_feature
            function = make_combined_feature_classifier
        print('handling', key)
        for i in progressbar(range(n)):
            clf = function(data, random_state=i, 
                vowel_stress_dict = vowel_stress_dict)
            _ = clf.classification_report()
            mccs[key].append(clf.mcc)
        print(key, 'done',np.mean(mccs[key]), np.std(mccs[key]), mccs[key])
    if save:
        if name: name = f'_{name}'
        filename = f'../mccs_density_clf_acoustic_correlates{name}.json'
        dict_to_json(mccs, filename)
    return mccs

def make_formant_classifier(stress_distance = None, random_state=42,
       vowel_stress_dict = None, verbose = False):
    if not stress_distance:
        if verbose:print('computing vowel formant distance to global mean')
        stress_distance = formants.make_vowel_f1f2_distance_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = stress_distance['stress']
    no_stress = stress_distance['no_stress']
    clf = Classifier(stress, no_stress, name = 'formant', 
        random_state=random_state)
    return clf
    
def make_intensity_classifier(intensities = None, random_state=42,
        vowel_stress_dict = None, verbose = False):
    if not intensities:
        if verbose:print('computing vowel intensities')
        intensities=intensity.make_vowel_intensity_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = intensities['stress']
    no_stress = intensities['no_stress']
    clf = Classifier(stress, no_stress, name = 'intensity', 
        random_state=random_state)
    return clf

def make_pitch_classifier(pitch = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not pitch: 
        if verbose:print('computing vowel pitch')
        pitch= pitch.make_vowel_pitch_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = pitch['stress']
    no_stress = pitch['no_stress']
    clf = Classifier(stress, no_stress, name = 'pitch', 
        random_state=random_state)
    return clf

def make_duration_classifier(durations = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not durations: 
        if verbose:print('computing vowel durations')
        durations = duration.make_vowel_duration_stress_dict(
            vowel_stress_dict = None)
    stress = durations['stress']
    no_stress = durations['no_stress']
    print('making classifier')
    clf = Classifier(stress, no_stress, name = 'duration', 
        random_state=random_state)
    return clf

def make_spectral_tilt_classifier(spectral_tilts = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not spectral_tilts: 
        if verbose: print('computing vowel spectral tilts')
        spectral_tilts = formants.make_dataset(
            vowel_stress_dict = vowel_stress_dict)
    X, y = spectral_tilts
    clf = frequency_band.train_lda(X, y, report = True, 
        random_state = random_state)
    return clf

def make_combined_feature_classifier(combined_feature = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not combined_feature: 
        if verbose: print('computing vowel combined feature')
        combined_feature = combined_features.make_dataset(
            vowel_stress_dict = vowel_stress_dict)
    X, y = combined_feature
    clf = combined_features.train_lda(X, y, report = True, 
        random_state = random_state)
    return clf

    

'''
def compute_mccs_with_ci(X,y, n = 100):
    compute MCCs for the combined features dataset
    mccs = {'combined':[]}
    for i in progressbar(range(n)):
        clf, data, report = train_lda(X, y, random_state = i)
        mccs['combined'].append(report['mcc'])
    print('done',np.mean(mccs['combined']), np.std(mccs['combined']))
    density_classifier.dict_to_json(mccs, 
        '../mccs_combined_features_lda_clf.json')
    return mccs
'''
