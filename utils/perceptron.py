import glob
import json
from utils import locations
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import os
from pathlib import Path
import pickle
from sklearn.metrics import matthews_corrcoef, accuracy_score
from sklearn.metrics import classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

removed_layers = [0,2,4,6,8,10,12,14,16,18,20,22]
layers = ['cnn',1,5,11,17,21,23]
sections = ['vowel', 'syllable', 'word']


def _train_mlp_classifier(X,y, random_state = 1, max_iter = 3000):
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
        stratify=y,random_state= random_state)
    clf=MLPClassifier(random_state=1,max_iter=max_iter)
    clf.fit(X_train, y_train)
    hyp = clf.predict(X_test)
    return y_test, hyp, clf

class Results:
    def __init__(self, y_test = None, hyp = None, result_filename = '',
        result_dict = {}, dataset_dict = {}, verbose = True, 
        results_type = 'stress', **kwargs):
        self.result_filename = result_filename
        self.path = Path(result_filename)
        self.y_test = y_test
        self.hyp = hyp
        self.result_dict = result_dict
        self.verbose = verbose
        if not y_test is None and not hyp is None: self._set_metrics()
        elif self.path.exists(): self._load_results()
        elif result_dict: self._set_results_from_dict()
        else:
            em = f'No results provided and no file found at {result_filename}'
            raise ValueError(em)
        self._handle_info(dataset_dict, kwargs)

    def _set_metrics(self):
        if self.verbose: print('computing metrics')
        self.accuracy = accuracy_score(self.y_test, self.hyp)
        self.mcc = matthews_corrcoef(self.y_test, self.hyp)
        self.report = classification_report(self.y_test, self.hyp)

    def _handle_info(self, dataset_dict, kwargs):
        keys = ['layer', 'section', 'name', 'n']
        for key in keys:
            if hasattr(self, key): continue
            if dataset_dict:
                if key in dataset_dict: setattr(self, key, dataset_dict[key])
            if kwargs:
                if key in kwargs: setattr(self, key, kwargs[key])
        not_handled = [k for k in kwargs if not hasattr(self, k)]
        if not_handled:
            print(f'Not handled in kwargs: {not_handled}')
        missing_info = [k for k in keys if not hasattr(self, k)]
        if missing_info:
            print(f'Missing info: {missing_info}')
            if self.verbose: print('setting info to None')
            for key in missing_info:
                setattr(self, key, None)

    def _load_results(self):
        if self.verbose: print('loading results from file')
        with open(self.result_filename, 'rb') as f:
            d = pickle.load(f)
        self.result_dict = d
        self.accuracy = d['accuracy']
        self.mcc = d['mcc']
        self.report = d['report']
        self.layer = d['layer']
        self.section = d['section']
        self.name = d['name']
        self.n = d['n']

    def to_dict(self):
        if self.result_dict: return self.result_dict
        self.result_dict = {'accuracy': self.accuracy, 'mcc': self.mcc, 
            'report': self.report}
        return self.result_dict
        
    def filename(self):
        if not self.result_filename:
            f = f'../results/{results_type}_{self.layer}_'
            f += f'{self.section}_{self.name}_{self.n}.json'
            self.result_filename = f
            self.path = Path(f)
        return self.result_filename

    def save(self, overwrite = False):
        if self.path.exists() and not overwrite:
            em = f'File {self.result_filename} exists. Use overwrite = True'
            raise ValueError(em)
        with open(self.result_filename, 'wb') as f:
            pickle.dump(self.to_dict(), f)


