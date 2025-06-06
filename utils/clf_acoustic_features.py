from audio import frequency_band, combined_features, formants
from datasets import acoustic_correlates
import numpy as np
from pathlib import Path
from utils import density_classifier, results, perceptron

feature_names = acoustic_correlates.feature_names
language_names = acoustic_correlates.language_names

def handle_cross_lingual(language_name, n_iterations = 20, overwrite = False,
    start = 0):
    '''computed classification results with classifiers trained on other
    language than the test data e.g. dutch clf and test data from english
    n_iterations: number of data split to run the classifier on the test data
    '''
    for other_langauge in language_names:
        print('handling', language_name, other_langauge)
        if other_langauge == language_name: continue
        handle_language(language_name, n_iterations,
            name = f'other-language-{other_langauge}', overwrite = overwrite,
            start = start)

def handle_language(language_name, n_iterations = 20, name ='', 
    overwrite = False, start = 0):
    '''computes classification results for all features for a language
    n_iterations: number of data split to run the classifier on the test data
    '''
    for i in range(start,n_iterations):
        random_state = i
        for feature_name in feature_names:
            _handle_feature(language_name, feature_name, random_state, 
            name = name, overwrite = overwrite)

def _handle_feature(language_name, feature_name, random_state = 42, 
    name = '', n = '', overwrite = False):
    '''computes classification results for a feature for a language
    name: name of the classifier e.g. 'other-language-dutch'
    '''
    data_type = 'stress'
    section = 'vowel'
    print('handling', language_name, feature_name, random_state, name)
    result_filename = results.make_result_filename(language_name, data_type, 
        feature_name, section, name, n,random_state)
    if not overwrite and Path(result_filename).exists():
        print(f'file {result_filename} exists. skipping')
        return
    if 'other-language' in name:
        other_language_name = name.split('-')[-1]
        dataset_filename = make_dataset_filename(other_language_name,
            feature_name)
        X, y = load_dataset(other_language_name, feature_name)
        clf = load_classifier(language_name, data_type, feature_name,
            section, name = '', n = n, random_state = random_state)
        hyp = clf.predict(X)
        y_test = y
    else:
        dataset_filename = make_dataset_filename(language_name, 
            feature_name)
        X, y = load_dataset(language_name, feature_name)
        function = feature_to_function[feature_name]
        y_test, hyp, clf = function(X, y, random_state = random_state)
        save_classifier(clf, language_name, data_type, feature_name,
            section, random_state = random_state)
    classifier_filename = make_classifier_filename(language_name,
        data_type, feature_name, section , random_state=random_state)
    result = results.save_results(y_test, hyp, language_name, data_type, 
        feature_name, section, rs = random_state, name = name, n = n,
        dataset_filename = dataset_filename, 
        classifier_filename = classifier_filename, overwrite = overwrite)
    return result

    

def duration_classifier(X,y, random_state=42,verbose = False, trim = True):
    print('training duration classifier')
    y_test, hyp, clf = _density_classifier(X, y, 'duration', random_state, 
        verbose, trim)
    return y_test, hyp, clf

def formant_classifier(X, y, random_state=42, verbose = False, trim = True):
    print('training formant classifier')
    y_test, hyp, clf = _density_classifier(X, y, 'formant', random_state,
        verbose, trim)
    return y_test, hyp, clf

def intensity_classifier(X, y, random_state=42, verbose = False, trim = True):
    print('training intensity classifier')
    y_test, hyp, clf = _density_classifier(X, y, 'intensity', random_state,
        verbose, trim)
    return y_test, hyp, clf

def pitch_classifier(X, y, random_state=42, verbose = False, trim = True):
    print(f'training pitch classifier')
    y_test, hyp, clf = _density_classifier(X, y, 'pitch', random_state,
        verbose, trim)
    return y_test, hyp, clf

def _density_classifier(X, y, name, random_state=42, verbose = False, 
    trim = True):
    print(f'training density classifier with random state {random_state}')
    clf = density_classifier.Classifier(X, y, name = name, 
        random_state=random_state)
    X_test, y_test = clf.X_test, clf.y_test
    hyp = clf.predict(X_test)
    if trim: clf = trim_classifier(clf)
    return y_test, hyp, clf

def spectral_tilt_classifier(X, y, random_state=42,verbose = False, 
    trim = True):
    print(f'training spectral tilt classifier with random state {random_state}')
    y_test, hyp, clf = frequency_band.train_lda(X, y, report = False, 
        random_state = random_state)
    if trim: clf = trim_classifier(clf)
    return y_test, hyp, clf

def combined_feature_classifier(X, y, random_state=42, verbose = False):
    print('training combined feature classifier')
    y_test, hyp, clf = combined_features.train_perceptron(X, y,  
        random_state = random_state)
    return y_test, hyp, clf

def load_dataset(language_name, feature_name):
    data = acoustic_correlates.load_dataset(language_name, feature_name)
    if not data:
        print(f'no data for {language_name} {feature_name}')
        return None
    X, y = data
    return np.array(X), np.array(y)

def make_dataset_filename(language_name, feature_name):
    f = acoustic_correlates.make_dataset_filename(language_name, feature_name)
    return f

def make_classifier_filename(language_name, data_type, layer, section,
    name = '', n = '', random_state = 1):
    f = perceptron.make_classifier_filename(language_name, data_type, layer, 
        section, name, n, random_state)

def load_classifier(language_name, data_type, layer, section, name = '', n = '',
    random_state = 1):
    return perceptron.load_classifier(language_name, data_type, layer, section, 
        name, n, random_state)

def save_classifier(clf, language_name, data_type, layer, section, name = '',
    n = '', random_state = 1):
    perceptron.save_classifier(clf, language_name, data_type, layer, section, 
        name, n, random_state)

def save_results(y_test, hyp, language_name, data_type, layer, section, 
    name, n, rs, dataset_filename, classifier_filename):
    result = perceptron.save_results(y_test, hyp, language_name, data_type, 
        layer, section, name, n, rs, dataset_filename, classifier_filename)
    return result

def trim_classifier(clf):
    '''removes bloated data from the classifier'''
    for attr in ['X','y','X_train','y_train', 'X_test','y_test']: 
        if hasattr(clf, attr): delattr(clf, attr)
    return clf

# map feature names to classification functions
feature_to_function = {
    'duration': duration_classifier,
    'formant': formant_classifier,
    'intensity': intensity_classifier,
    'pitch': pitch_classifier,
    'spectral-tilt': spectral_tilt_classifier,
    'combined-features': combined_feature_classifier}
