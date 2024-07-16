'''
module to create a classifier based on the density of a feature
for stressed and unstressed vowels.

features:
- formants
- intensity
- pitch
- duration
'''

import formants
from general import dict_to_json
import stress_intensity_diff as sid
import stress_pitch_diff as spd
import stress_duration_diff as sdd
import stress_spectral_diff as ssd
import frequency_band as fb
import numpy as np
from progressbar import progressbar
from scipy import stats
from sklearn.metrics import classification_report, matthews_corrcoef
from sklearn.model_selection import train_test_split
import word


def compute_mccs_with_ci(n = 100, formant_data = None, intensities = None,
    pitch = None, durations = None, w = None):
    mccs = {'formant':[], 'intensity':[], 'pitch':[], 'duration':[]}
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
        print('computing', key)
        for i in progressbar(range(n)):
            clf = function(data, w = w, random_state=i)
            _ = clf.classification_report()
            mccs[key].append(clf.mcc)
        print(key, 'done',np.mean(mccs[key]), np.std(mccs[key]), mccs[key])
    dict_to_json(mccs, 'mccs_density_clf_acoustic_correlates.json')
    return mccs

            
            

def make_formant_classifier(stress_distance = None, w = None, random_state=42):
    if not stress_distance:
        stress_distance = formants.compute_distance_to_global_mean(w = w)
    stress = stress_distance['stressed']['distance']
    no_stress = stress_distance['unstressed']['distance']
    clf = Classifier(stress, no_stress, name = 'formant', 
        random_state=random_state)
    return clf
    
def make_intensity_classifier(intensities = None, w = None, random_state=42):
    if not intensities: intensities = sid.get_intensity_from_vowels(w = w)
    stress = intensities['stress']
    no_stress = intensities['no stress']
    clf = Classifier(stress, no_stress, name = 'intensity', 
        random_state=random_state)
    return clf

def make_pitch_classifier(pitch = None, w = None, random_state=42):
    if not pitch: pitch = spd.load_pitch_json()
    stress, no_stress = spd._find_stressed_unstressed(pitch[1:])
    clf = Classifier(stress, no_stress, name = 'pitch', 
        random_state=random_state)
    return clf

def make_duration_classifier(durations = None, w = None, random_state=42):
    if not durations: durations = sdd.get_durations_from_vowels(w = w)
    stress = durations['stress']
    no_stress = durations['no stress']
    clf = Classifier(stress, no_stress, name = 'duration', 
        random_state=random_state)
    return clf

class Classifier:
    def __init__(self, stress, no_stress, name = '', random_state=42, 
        verbose=False):
        self.stress=stress 
        self.no_stress=no_stress 
        self.name = name
        self.random_state = random_state
        self.verbose = verbose
        self._train()

    def _train(self, test_size=0.33):
        self.X, self.y = make_dataset(self.stress, self.no_stress)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X,self.y, test_size = test_size, 
            random_state=self.random_state)
        stress_indices = np.where(self.y_train == 1)
        no_stress_indices = np.where(self.y_train == 0)
        self.stress_kde = stats.kde.gaussian_kde(self.X_train[stress_indices])
        self.no_stress_kde = stats.kde.gaussian_kde(
            self.X_train[no_stress_indices])
        
    def predict(self, X):
        stress = self.stress_kde(X)
        no_stress = self.no_stress_kde(X)
        output = np.array([no_stress, stress])
        return np.argmax(output,0)

    def classification_report(self):
        if hasattr(self, '_report'): return self._report
        self.hyp = self.predict(self.X_test)
        self.cr = classification_report(self.y_test, 
            self.hyp)
        self.mcc = matthews_corrcoef(self.y_test, self.hyp)
        if self.verbose:
            print('classifier:', self.name)
            print(self.cr)
            print('MCC:', matthews_corrcoef(self.y_test, self.hyp))
        self._report = {'classification_report': self.cr,
                        'mcc': self.mcc}
        return self._report

def make_dataset(stress, no_stress):
    X = np.concatenate([stress, no_stress])
    y = np.concatenate([np.ones(len(stress)), np.zeros(len(no_stress))])
    return X, y

