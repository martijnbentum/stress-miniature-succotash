import json
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
from utils.results import Results, to_mccs, _to_mcc_dict
from utils import stats

def save_dict_to_json(d, path):
    with open(path, 'w') as f:
        json.dump(d, f)

def results_to_mcc_dict(results = None, result_type = 'stress', 
    section = 'vowel', mcc_dict = {}, save = False):
    '''aggregate mccs from results to mcc_dict
    the mccs are based on perceptrons trained on the layers in the wav2vec 2.0
    model
    '''
    if not results:
        results = Results()
    for language_name in results.languages:
        for layer in results.layers:
            results_list = results.select_results(language_name, result_type,
                layer, section)
            if not results_list:
                m = f'No results for {language_name} {result_type} '
                m += f'{layer} {section}, skipping'
                print(m)
                continue
            mccs = to_mccs(results_list)
            _to_mcc_dict(mccs, language_name, layer, mcc_dict)
    if save:
        filename = f'../results/mccs_{result_type}_{section}.json'
        save_dict_to_json(mcc_dict, filename)
    return mcc_dict

def load_acoustic_correlates_mccs(language_name = 'dutch', 
    section = 'vowel', mcc_dict = {}):
    mcc_dict[language_name] = {}
    filename = f'../results/{language_name}_{section}_mccs_'
    filename += 'clf_acoustic_correlates.json'
    if not Path(filename).exists(): 
        print(f'{filename} does not exist')
        return
    with open(filename) as f:
        d = json.load(f)
    for key in d.keys():
        mcc_dict[language_name][key] = {}
        mean, sem, ci = stats.compute_mean_sem_ci(d[key])
        mcc_dict[language_name][key]['mean'] = mean
        mcc_dict[language_name][key]['sem'] = sem
        mcc_dict[language_name][key]['ci'] = ci
        mcc_dict[language_name][key]['mccs'] = d[key]
    return mcc_dict

def _combine_on_language(acoustic_d,wav2vec_d, classifier_order = []):
    if not classifier_order:
        o = 'duration,intensity,pitch,formant,spectral tilt,combined features'
        o += ',codevector,cnn,5,11,17,23'
        classifier_order = o.split(',')
    output = {}
    languages = list(acoustic_d.keys()) + list(wav2vec_d.keys())
    for language in languages:
        output[language] = {}
        if language in acoustic_d.keys():
            for classifier in classifier_order:
                if classifier in acoustic_d[language].keys():
                    output[language][classifier] = acoustic_d[language][classifier]
        if language in wav2vec_d.keys():
            for classifier in classifier_order:
                if classifier in wav2vec_d[language].keys():
                    output[language][classifier] = wav2vec_d[language][classifier]
    return output
    

def combine_acoustic_wav2vec_mccs(acoustic_mcc_dict = None,
    wav2vec_mcc_dict = None, classifier_order = []):
    if not wav2vec_mcc_dict:
        with open('../results/mccs_stress_vowel.json') as f:
            wav2vec_mcc_dict= json.load(f)
    if not acoustic_mcc_dict:
        acoustic_mcc_dict = {}
        for language_name in wav2vec_mcc_dict.keys():
            acoustic_mcc_dict = load_acoustic_correlates_mccs(
                language_name = language_name, mcc_dict = acoustic_mcc_dict)
    return _combine_on_language(acoustic_mcc_dict, wav2vec_mcc_dict, 
        classifier_order = classifier_order)

    
    
    

def _plot_language_mccs(mcc_result_dict, language_name = 'dutch', 
    new_figure = True, offset = 0, color = 'black'):
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    d = mcc_result_dict[language_name]
    x = np.arange(len(d)) + offset
    means = [d[layer]['mean'] for layer in d.keys()]
    cis = [d[layer]['ci'] for layer in d.keys()]
    plt.errorbar(x, means, yerr = cis, label = language_name, markersize = 12,
        color = color, fmt = ',', elinewidth = 2.5, capsize = 9, 
        capthick = 1.5)
    if abs(x[0]) < 0.01:
        plt.xticks(x, d.keys(), rotation = 45)
    plt.ylabel('Matthews correlation coefficient')

def _plot_vertical_lines(n_categories, width = 1):
    x = np.arange(n_categories)
    offset = width / 2
    for i in range(n_categories):
        if i % 2 == 0:
            plt.axvspan(x[i] - offset, x[i] + offset, color = 'grey', 
                alpha = .1) 
    
def plot_mccs(mcc_result_dict = None, new_figure = True, 
    language_names = []):
    if not mcc_result_dict:
        with open('../results/mccs_stress_vowel.json') as f:
            mcc_result_dict = json.load(f)
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    n_languages = len(mcc_result_dict.keys())
    delta_offset = 1 / n_languages
    offset = 0 - delta_offset if n_languages % 2 == 0 else 0 - delta_offset * 2
    colors = plt.get_cmap('tab10').colors
    if not language_names: language_names = mcc_result_dict.keys()
    for i,language in enumerate(language_names):
        print('plotting', language)
        _plot_language_mccs(mcc_result_dict, language, new_figure = False, 
            offset = offset, color = colors[i])
        offset += delta_offset
    n_categories = len(mcc_result_dict[language].keys())
    _plot_vertical_lines(n_categories)
    plt.legend()
    plt.grid(alpha = .5, axis = 'y')

        
