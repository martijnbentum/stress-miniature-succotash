import matplotlib.pyplot as plt
import numpy as np
from progressbar import progressbar
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import classification_report
from sklearn.metrics import matthews_corrcoef
from sklearn.model_selection import train_test_split

def make_lda_report(clf, X_test, y_test):
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
    data = {'X_train': X_train, 'X_test': X_test, 'y_train': y_train}
    if report: report = make_lda_report(clf, X_test, y_test)
    else: report = None
    return clf, data, report

def plot_lda_hist(X, y, clf = None, new_figure = True, 
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = '', xlim = None):
    X, y = np.array(X), np.array(y)

    if not clf:
        clf, _, _ = train_lda(X, y, report = False)

    plt.ion()
    if new_figure: plt.figure()
    ax = plt.gca()
    if minimal_frame:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    if ylim: plt.ylim(ylim)
    if xlim: plt.xlim(xlim)
    tf = clf.transform(X)
    plt.hist(tf[y==1], bins = 50, alpha=1, color = 'black',
        label = 'stress')
    plt.hist(tf[y==0], bins = 50, alpha=0.7, color = 'orange',
        label = 'no stress')

    if add_legend: plt.legend()
    plt.xlabel(xlabel)
    if add_left: plt.ylabel('Counts')
    else:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left = False)
        ax.set_yticklabels([])
    plt.grid(alpha=0.3)
    if not xlabel: xlabel = 'Linear Discriminant score'
    plt.xlabel(xlabel)
    plt.show()
