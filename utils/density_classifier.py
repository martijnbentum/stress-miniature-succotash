'''
module to create a classifier based on the density of a feature
for stressed and unstressed vowels.

1d features:
- formants (distance to global mean)
- intensity
- pitch
- duration
'''

import json
import numpy as np
from progressbar import progressbar
from scipy import stats
from sklearn.metrics import classification_report, matthews_corrcoef
from sklearn.model_selection import train_test_split

class Classifier:
    '''classifier based on the density of a feature for stressed and
    unstressed vowels.
    '''
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
    '''create a dataset for the density classifier.
    '''
    X = np.concatenate([stress, no_stress])
    y = np.concatenate([np.ones(len(stress)), np.zeros(len(no_stress))])
    return X, y

def dict_to_json(d, filename):
    '''save a dictionary to a json file.
    '''
    with open(filename, 'w') as f:
        json.dump(d, f)

