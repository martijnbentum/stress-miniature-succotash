import matplotlib.pyplot as plt
import numpy as np
from progressbar import progressbar
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import classification_report
from sklearn.metrics import matthews_corrcoef
from sklearn.model_selection import train_test_split
from utils import plot_distributions

def make_lda_report(clf, X_test, y_test):
    '''make a classification report for an LDA classifier
    with precision, recall, f1, and mcc scores
    '''
    y_pred = clf.predict(X_test)
    cr = classification_report(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    report = {'classification_report': cr, 'mcc': mcc}
    return report
    
def train_lda(X, y, test_size = 0.33, report = True, random_state = 42):
    '''train an LDA based on the vowel spectral balance datase
    use make_dataset function to create the dataset (X, y)
    '''
    X_train, X_test, y_train, y_test = train_test_split(
        X,y, test_size = test_size, random_state=random_state)
    clf = LinearDiscriminantAnalysis()
    clf.fit(X_train, y_train)
    hyp = clf.predict(X_test)
    return y_test, hyp, clf 

def plot_lda_hist(X, y, clf = None, new_figure = True, 
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = '', xlim = None, plot_density = False):
    '''plot distribution of LDA scores for stress and no stress vowels'''
    X, y = np.array(X), np.array(y)
    if not clf:
        clf, _, _ = train_lda(X, y, report = False)
    tf = clf.transform(X)
    d = {}
    d['stress'] = tf[y==1].ravel()
    d['no_stress'] = tf[y==0].ravel()
    plot_distributions.plot_stress_no_stress_distributions(d, 
        new_figure = new_figure, minimal_frame = minimal_frame,
        ylim = ylim, add_left = add_left, add_legend = add_legend,
        bins = bins, xlabel = xlabel, xlim = xlim, 
        plot_density = plot_density)


