import glob
import json
from utils import locations
import numpy as np
import os
import pickle
from sklearn.metrics import matthews_corrcoef, accuracy_score
from sklearn.metrics import classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from matplotlib.patches import Patch

removed_layers = [0,2,4,6,8,10,12,14,16,18,20,22]
layers = ['cnn',1,5,11,17,21,23]
sections = ['vowel', 'syllable', 'word']


def _train_mlp_classifier(X,y, random_state = 1):
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
        stratify=y,random_state= random_state)
    clf=MLPClassifier(random_state=1,max_iter=300)
    clf.fit(X_train, y_train)
    hyp = clf.predict(X_test)
    return y_test, hyp, clf

