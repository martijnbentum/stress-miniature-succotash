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
    
def compute_mccs_with_ci(X,y, n = 100):
    '''
    compute MCCs for the combined features dataset
    '''
    mccs = {'combined':[]}
    for i in progressbar(range(n)):
        clf, data, report = lda.train_lda(X, y, report = True, random_state = i)
        mccs['combined'].append(report['mcc'])
    print('done',np.mean(mccs['combined']), np.std(mccs['combined']))
    density_classifier.dict_to_json(mccs, 
        '../mccs_combined_features_lda_clf.json')
    return mccs


    
