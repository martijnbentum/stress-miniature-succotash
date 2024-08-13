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

def train_all_word_classifiers(stress_info = None, layers = layers, 
    n_classifiers = 100): 
    '''train mlp classifiers based on the data structure hidden_states.'''
    if not stress_info: stress_info = Info(dataset_name = 'mald_all')
    for layer in layers:
        for i in range(2,n_classifiers + 2):
            print('starting on',layer, i)
            train_classifier_all_words(stress_info, layer = layer, 
                random_state = i)

def train_classifier_all_words(stress_info, name = 'mald-all' , 
    layer = 'cnn', overwrite = False,random_state = 1):
    f=locations.all_words_stress_perceptron_dir + 'clf_' + name + '_vowel'
    f+= '_' + str(layer) + '_rs-' + str(random_state) + '.pickle'
    if os.path.isfile(f) and not overwrite:
        print(f, 'already exists, skipping')
    print('starting on',f)
    X, y = stress_info.xy(layer = layer, section = 'vowel')
    y_test, hyp, clf = _train_mlp_classifier(X,y, random_state)
    save_performance(y_test, hyp, name, layer, 'vowel', random_state,
        directory = locations.all_words_stress_perceptron_dir)
        
    with open(f, 'wb') as fout:
        pickle.dump(clf,fout)

def train_classifier(stress_info, name , layer, section, overwrite = False,
    random_gt = False, occlusion_type = None, random_state = 1):
    '''train mlp classifier based on the data structure hidden_states.
    name            info for in the filename (wav2vec model pretrained)
    layer           layer of wav2vec 2.0 to use
    section         section of the data to use (vowel, syllable, word)
    overwrite       if True, overwrite existing files
    random_gt       if True, use random ground truth (sanity check)
    occlusion_type  if not None, use occluded data (all audio outside
                    vowel or syllable is set to 0)
    random_state    random state for train_test_split
                    used for the ccn tf (transformer) comparison
    '''
    if name: name = '_' + name
    if random_gt: name += '-random-gt'
    if occlusion_type: name += '-occlusion-' + occlusion_type
    if random_state != 1: 
        name += '_rs-' + str(random_state)
        f=locations.cnn_tf_comparison_dir+ 'clf' + name + '_' + section   
    else:
        f=locations.stress_perceptron_dir + 'clf' + name + '_' + section   
    f+= '_' + str(layer) + '.pickle'
    if os.path.isfile(f) and not overwrite:
        print(f, 'already exists, skipping')
        return
    print('starting on',f)
    X, y = stress_info.xy(layer = layer, section = section, 
        random_gt = random_gt, occlusion_type = occlusion_type)
    y_test, hyp, clf = _train_mlp_classifier(X,y, random_state)
    save_performance(y_test, hyp, name, layer, section, random_state)
        
    with open(f, 'wb') as fout:
        pickle.dump(clf,fout)


def train_classifiers(stress_info, name = '', layers = layers, 
    sections = sections, random_gt = False, occlusion_type = None,
    random_state = 1):
    '''train mlp classifiers based on the data structure hidden_states.'''
    for layer in layers:
        for section in sections:
            train_classifier(stress_info, name, layer, section, 
                random_gt = random_gt, occlusion_type = occlusion_type,
                random_state = random_state)

def train_mlp_for_cnn_tf_comparison(stress_info, name, layers = layers,
    occlusion_type = None, n_classifiers = 100):
    '''a difference was observed between the mlp trained on the cnn 
    and the transformer layers. This function trains multiple mlp's
    to see if this difference is consistent.'''
    if occlusion_type: sections = [occlusion_type]
    else: sections = ['vowel', 'syllable']
    for i in range(2,n_classifiers + 2):
        train_classifiers(stress_info, name, layers, sections,
        occlusion_type = occlusion_type, random_state = i)


def train_all_mlp_for_cnn_tf_comparison(stress_info,name,n_classifiers = 100):
    '''see train_mlp_for_cnn_tf_comparison
    wrapper function to call the difference occlusion types.
    '''
    for occlusion_type in [None,'vowel', 'syllable']:
        train_mlp_for_cnn_tf_comparison(stress_info, name, 
            occlusion_type = occlusion_type, n_classifiers = n_classifiers)
    

def save_performance(gt, hyp, name, layer, section, random_state, 
    directory = None):
    d = {}
    d['mcc'] = round(matthews_corrcoef(gt, hyp), 3)
    d['accuracy'] = round(accuracy_score(gt, hyp), 3)
    d['report'] = classification_report(gt, hyp)
    print(name, layer, section)
    for k,v in d.items():
        print(k,v)
    print('---')
    rs = ''
    if directory:
        if random_state != 1:rs = '_rs-' + str(random_state)
        f = directory + 'score_' + name 
    elif random_state != 1: 
        rs = '_rs-' + str(random_state)
        f = locations.cnn_tf_comparison_dir + 'score' + name 
    else: 
        f = locations.stress_perceptron_dir + 'score' + name 
    f +=  '_' + str(layer)+'_'+ section + rs + '.json'
    with open(f, 'w') as fout:
        json.dump(d, fout)
    return d



class Perceptron:
    '''class to hold layer specific classifiers.'''
    def __init__(self, filename = None, layers = layers):
        self.layers = layers
        self.filename = filename
        c = [load_perceptron(l,small,ctc, filename) for l in layers]
        self.classifiers = c


def score_filename_to_layer_section(f):
    if not '_rs-' in f:
        section = f.split('_')[-1].split('.')[0]
        layer = f.split('_')[-2]
        return layer, section
    else:
        random_state = f.split('-')[-1].split('.')[0]
        section = f.split('_')[-2]
        layer = f.split('_')[-3]
        return layer, section, random_state


def get_scores(name, layer = '*', section = '*', occlusion = False,
    directory = locations.stress_perceptron_dir, random_state = ''):
    f = directory+ 'score_' + name 
    if occlusion: f += '-occlusion*'
    f +=  '_' + str(layer) +'_'+ section + random_state + '.json'
    fn = glob.glob(f)
    output = {}
    for f in fn:
        key = score_filename_to_layer_section(f)
        with open(f, 'r') as fin:
            d = json.load(fin)
        output[key] = d
    return output

def get_cnn_tf_scores(name, layer = '*', section = '*', occlusion = False,
    directory = locations.cnn_tf_comparison_dir, random_state = ''):
    if type(random_state) == int: random_state = '_rs-' + str(random_state)
    elif random_state == '': random_state = '*'
    return get_scores(name, layer, section, occlusion, directory, random_state)
    

def show_scores(name, section):
    f = locations.stress_perceptron_dir + 'score_' + name 
    f +=  '_*_'+ section + '.json'
    fn = glob.glob(f)
    for f in fn:
        print(f)
        with open(f, 'r') as fin:
            d = json.load(fin)
        print('mcc', d['mcc'])
        print('---')

def show_cnn_tf_scores(name, section, occlusion = False):
    f = locations.cnn_tf_comparison_dir+ 'score_' + name 
    if occlusion: f += '-occlusion*'
    f +=  '_*_'+ section + '*.json'
    fn = glob.glob(f)
    for f in fn:
        print(f)
        with open(f, 'r') as fin:
            d = json.load(fin)
        print('mcc', d['mcc'])
        print('---')

def plot_scores(name = 'mald-variable-stress-small-pretrained', 
    occlusion =False):
    '''plot the mcc scores for the mlps trained on the wav2vec hidden states
    compares performance between mlps trained on vowel syllable and word
    also shows performance for random labels as a sanity check
    '''
    scores= get_scores(name, occlusion = occlusion)
    print(scores.keys())
    mcc_vowel= [scores[str(layer),'vowel']['mcc'] for layer in layers]
    mcc_syllable= [scores[str(layer),'syllable']['mcc'] for layer in layers]
    if not occlusion:
        mcc_word = [scores[str(layer),'word']['mcc'] for layer in layers]
    plt.clf()
    plt.ylim(-0.1,1)
    plt.plot(mcc_vowel, label = 'vowel')
    plt.plot(mcc_syllable, label = 'syllable')
    if not occlusion:
        plt.plot(mcc_word, label = 'word')
    plt.legend()
    plt.grid(alpha = 0.3)
    plt.xticks(range(len(layers)), layers)
    plt.xlabel('wav2vec 2.0 layer')
    plt.ylabel('matthews correlation coefficient')
    plt.show()

def compute_mean_and_sem(d, section):
    '''compute the mean and standard error of the mean for the mcc scores.'''
    all_mccs = []
    means = []
    sems = []
    stds = []
    for layer in layers:
        mccs=[d[str(layer),section, str(rs)]['mcc'] for rs in range(2,102)]
        means.append( np.mean(mccs) )
        stds.append( np.std(mccs) )
        sems.append( np.std(mccs)/np.sqrt(len(mccs)) )
        all_mccs.append(mccs)
    cis = [2.576 * sem for sem in sems]
    return means, stds, sems, cis, all_mccs
        
def _add_errorbars(sno, so, section, add_legend = False):
    '''add errorbars to the plot_cnn_tf_comparison plot'''
    x = range(len(layers))
    means, stds, sems, cis, _ = compute_mean_and_sem(sno, section)
    plt.errorbar(x, means, yerr = cis, fmt = ',', markersize = 15, 
        color = 'black',
        elinewidth = 2.5, capsize = 9, capthick = 1,label = 'no occlusion')
    means, stds, sems, cis, _ = compute_mean_and_sem(so, section)
    plt.errorbar(x, means, yerr = cis, fmt = ',', markersize = 12, 
        color = 'orange', 
        elinewidth = 2.5, capsize = 9, capthick = 1,label = 'occlusion')
    if add_legend:
        legend = plt.legend()



def plot_cnn_tf_comparison(name = 'comparison', section = 'vowel',
    add_errorbars = True, add_lines = True, aspect = 6, 
    add_all_words = False):
    '''plot the mcc scores for the mlps trained on the wav2vec hidden states
    compares performance between occluded audio input and non occluded audio
    occluded audio, everything besides the vowel or syllable is set to 0.
    '''
    sno= get_cnn_tf_scores(name, occlusion = False)
    so= get_cnn_tf_scores(name, occlusion = True)
    plt.clf()
    plt.ylim(0.5,1)
    argsno = {'label':'no occlusion','alpha':0.1,'color':'navy'}
    argso = {'label':'occlusion','alpha':0.1,'color':'darkorange'}
    if add_lines:
        for rs in range(2,102):
            mcc_no=[sno[str(layer),section,str(rs)]['mcc'] for layer in layers]
            mcc_o= [so[str(layer),section,str(rs)]['mcc'] for layer in layers]
            l1 = plt.plot(mcc_no, **argsno) 
            l2 = plt.plot(mcc_o, **argso) 
            argsno['label'] = None
            argso['label'] = None
        legend = plt.legend()
        for handle in legend.legendHandles:
            handle.set_alpha(1)
    plt.grid(alpha = 0.3)
    plt.xticks(range(len(layers)), layers)
    plt.xlabel('wav2vec 2.0 layer')
    plt.ylabel("matthew's correlation coefficient")
    add_legend = not add_lines
    if add_all_words:
        results = load_all_word_results()
        add_errorbars_all_words(results)
    if add_errorbars:
        _add_errorbars(sno, so, section, add_legend)
    if aspect:
        plt.gca().set_aspect(aspect)
    plt.show()
    
def _compute_mean_and_sem_all_words(results):
    means, stds, sems, all_mccs = [],[],[],[]
    for layer in layers:
        mccs = [results[str(layer), rs]['mcc'] for rs in range(2,102)]
        means.append( np.mean(mccs) )
        stds.append( np.std(mccs) )
        sems.append( np.std(mccs)/np.sqrt(len(mccs)) )
        all_mccs.append(mccs)
    cis = [2.576 * sem for sem in sems]
    return means, stds, sems, cis, all_mccs

def add_errorbars_all_words(results):
    '''add errorbars to the all words result plot'''
    x = range(len(layers))
    means, stds, sems, cis, _ = _compute_mean_and_sem_all_words(results)
    plt.errorbar(x, means, yerr = cis, fmt = ',', markersize = 15, 
        color = 'grey',
        elinewidth = 2.5, capsize = 9, capthick = 1, 
        label = 'complete dataset')

def plot_all_word_scores():
    '''plot the mcc scores for the mlps trained on the wav2vec hidden states
    for all words
    '''
    results = load_all_word_results()
    plt.ion()
    plt.figure()
    plt.ylim(0.5,1)
    '''
    for rs in range(2,102):
        mccs=[results[str(layer),rs]['mcc'] for layer in layers]
        l1 = plt.plot(mccs, alpha = 0.1, color = 'black') 
    '''
    plt.grid(alpha = 0.3)
    plt.xticks(range(len(layers)), layers)
    plt.xlabel('wav2vec 2.0 layer')
    plt.ylabel("matthew's correlation coefficient")
    add_errorbars_all_words(results)
    plt.show()


def _stringify_keys(d):
    output = {}
    for key, value in d.items():
        output['-'.join(key)] = value
    return output
    

def _save_cnn_tf_comparison():
    sno= _stringify_keys(get_cnn_tf_scores('comparison', occlusion = False))
    so= _stringify_keys(get_cnn_tf_scores('comparison', occlusion = True))
    d = {'no oclussion':sno, 'occlusion':so}
    with open(locations.ld_base + 'cnn_tf_comparison.json', 'w') as fout:
        json.dump(d, fout)
    return d
