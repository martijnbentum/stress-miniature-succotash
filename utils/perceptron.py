from utils import locations
from pathlib import Path
import pickle
from progressbar import progressbar
from utils import results
from sklearn.metrics import matthews_corrcoef, accuracy_score
from sklearn.metrics import classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

removed_layers = [0,2,4,6,8,10,12,14,16,18,20,22]
layers = ['cnn',1,5,11,17,21,23]
sections = ['vowel', 'syllable', 'word']

def train_mlp_classifier(X,y, random_state = 1, max_iter = 3000):
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
        stratify=y,random_state= random_state)
    clf=MLPClassifier(random_state=1,max_iter=max_iter)
    clf.fit(X_train, y_train)
    hyp = clf.predict(X_test)
    return y_test, hyp, clf

def handle_classifier_training(language_name, data_type, layer, section, 
    name = '', n = '', rs = 1, max_iter = 3000, data_dict = None):
    if data_dict is None:
        print('loading dataset')
        d = load_dataset(language_name, data_type, layer, section, name, n)
    X, y = d['X'], d['y']
    print('training classifier')
    y_test, hyp, clf = train_mlp_classifier(X, y, random_state = rs, 
        max_iter = max_iter)
    classifier_filename = make_classifier_filename(language_name, 
        data_type, layer, section, name, n, rs)
    dataset_filename = make_dataset_filename(language_name, data_type, layer, 
        section, name, n)
    result = results.Result(y_test = y_test, hyp = hyp, 
        language_name = language_name,
        layer = layer, section = section, name = name, n = n, 
        random_state = rs, result_type = data_type,
        dataset_filename = dataset_filename, 
        classifier_filename = classifier_filename)
    print(result)
    result.save()
    save_classifier(clf, language_name, data_type, layer, section, name, n, rs)
    print('saved classifier and result')
    return clf, result

def train_multiple_classifiers(language_name, data_type, layers, sections,
    number_classifiers = 20, name = '', n = '', max_iter = 3000,
    overwrite = False, start_index = 0):
    for i in progressbar(range(start_index,number_classifiers)):
        for layer in layers:
            for section in sections:
                classifier_filename = make_classifier_filename(language_name, 
                    data_type, layer, section, name, n, i)
                path = Path(classifier_filename)
                if path.exists() and not overwrite: 
                    print(f'file {classifier_filename} exists. skipping')
                    continue
                print(f'training classifier {classifier_filename}')
                clf, result = handle_classifier_training(language_name, 
                    data_type, layer, section, name = name, n = n, rs = i, 
                    max_iter = max_iter)

def handle_language_stress(language_name, layers = None, sections = None,
    number_classifiers = 20, overwrite = False, start_index = 0):
    if not layers: layers = ['codevector', 'cnn', 5, 11, 17, 23]
    if not sections: sections = ['vowel']
    print(f'training classifiers for {language_name} stress')
    print(f'layers: {layers} sections: {sections}')
    train_multiple_classifiers(language_name, 'stress', layers, sections,
        number_classifiers = number_classifiers, overwrite = overwrite,
        start_index = start_index)
    

def make_classifier_filename(language_name, data_type, layer, section,
    name = '', n = '', random_state = 1):
    f = f'../classifiers/clf_{language_name}_{data_type}_{layer}_{section}'
    f += f'_{name}_{n}_{random_state}.pickle'
    return f
    
def save_classifier(clf, language_name, data_type, layer, section, name = '',
    n = '', random_state = 1):
    filename = make_classifier_filename(language_name, data_type, layer, 
        section, name, n, random_state)
    with open(filename, 'wb') as f:
        pickle.dump(clf, f)

def load_dataset(language_name, data_type, layer, section, name = '', n = ''): 
    filename = make_dataset_filename(language_name, data_type, layer, section, 
        name, n)
    with open(filename,'rb') as f:
        d = pickle.load(f)
    return d

def make_dataset_filename(language_name, data_type, layer, section, 
    name = '', n = ''):
    f = f'../dataset/xy_dataset-{data_type}_language-{language_name}_'
    f += f'section-{section}_layer-{layer}_n-{n}_name-{name}.pickle'
    return f
