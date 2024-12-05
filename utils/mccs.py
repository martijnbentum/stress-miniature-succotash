import json
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
from utils import stats

language_names = ['dutch', 'english', 'german', 'polish', 'hungarian']
classifier_order = ['duration', 'intensity', 'pitch', 'formant',
    'spectral-tilt', 'combined-features', 'codevector', 'cnn', 5, 11, 
    17, 23]
        
def load_results(return_stats = True):
    with open('../results.json') as f:
        d = json.load(f)
    if return_stats: return results_to_stats(d)
    return d

def _result_to_identifier(result):
    language_name = result['language_name']
    layer = result['layer']
    name = result['name']
    if not name: return f'{language_name}-{layer}'
    return f'{language_name}-{layer}-{name}'

def results_to_stats(results):
    output = {}
    for result in results:
        identifier = _result_to_identifier(result)
        language_name = result['language_name']
        layer = result['layer']
        mcc = result['mcc']
        name = result['name']
        if identifier not in output: 
            output[identifier] = {'language_name': language_name, 
                'layer': layer, 'name': name, 'mccs': [mcc]}
        else:
            output[identifier]['mccs'].append(mcc)
    o = []
    for key, item in output.items():
        item['mean'], item['sem'], item['ci'] = stats.compute_mean_sem_ci(
            item['mccs'])
        item['mccs'] = [round(x, 3) for x in item['mccs']]
        item['identifier'] = key
        o.append(item)
    return o 

def filter_cross_lingual(cross_lingual = True):
    results = load_results()
    output = []
    for result in results:
        if cross_lingual:
            if 'other-language-' in result['name']:
                output.append(result)
        else:
            if not 'other-language-' in result['name']:
                output.append(result)
    return output

def filter_language(language_name, cross_lingual = False):
    results = load_results()
    results = filter_cross_lingual(cross_lingual)
    output = []
    for result in results:
        if language_name == result['language_name']:
            output.append(result)
    output = sorted(output, key = lambda x: classifier_order.index(x['layer']))
    return output

def filter_other_language(language_name, other_language_name):
    results = filter_language(language_name, cross_lingual = True)
    output = []
    for result in results:
        if other_language_name in result['name']:
            output.append(result)
    output = sorted(output, key = lambda x: classifier_order.index(x['layer']))
    return output

def plot_language_mccs(language_name = 'dutch', new_figure = True, 
    offset =0, color = 'black', plot_grid = True, results = None, 
    error_alpha = 1, prepend_label = ''):
    if not results: results = filter_language(language_name) 
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    x = np.arange(len(results)) + offset
    x_tick_names = [result['layer'] for result in results]
    print(x_tick_names)
    try:x_tick_names[x_tick_names.index('combined-features')] = 'combined'
    except:return
    means = [result['mean'] for result in results]
    cis = [result['ci'] for result in results]
    plt.errorbar(x, means, yerr = cis, label = prepend_label + language_name, 
        markersize = 12,
        color = color, fmt = ',', elinewidth = 1.5, capsize = 3, 
        capthick = 1.5, alpha = error_alpha)
    if abs(x[0]) < 0.01:
        plt.xticks(x, x_tick_names, rotation = 90)
    plt.ylabel('Matthews correlation coefficient')
    if plot_grid: plt.grid(alpha = .5) 
    plt.tight_layout()

def _plot_vertical_lines(n_categories, width = 1):
    x = np.arange(n_categories)
    offset = width / 2
    for i in range(n_categories):
        if i % 2 == 0:
            plt.axvspan(x[i] - offset, x[i] + offset, color = 'grey', 
                alpha = .1) 
    
def plot_mccs(new_figure = True, languages= []):
    plt.ion()
    if new_figure: plt.figure()
    if not languages: languages = language_names
    plt.ylim(0,1)
    n_languages = len(languages)
    delta_offset = 1 / n_languages
    offset = 0 - delta_offset if n_languages % 2 == 0 else 0 - delta_offset * 2
    colors = plt.get_cmap('tab10').colors
    for i,language in enumerate(language_names):
        print('plotting', language)
        plot_language_mccs(language, new_figure = False, 
            offset = offset, color = colors[i], plot_grid = False)
        offset += delta_offset
    n_categories = len(classifier_order)
    _plot_vertical_lines(n_categories)
    plt.legend()
    plt.grid(alpha = .5, axis = 'y')

def plot_cross_lingual(language_name = 'dutch', new_figure = True):
    plt.ion()
    if new_figure: plt.figure()
    languages = language_names
    plt.ylim(0,1)
    n_languages = len(languages)
    other_languages = [x for x in language_names if x != language_name]
    delta_offset = 1 / n_languages
    offset = 0 - delta_offset if n_languages % 2 == 0 else 0 - delta_offset * 2
    colors = plt.get_cmap('tab10').colors
    for i,language in enumerate(language_names):
        print('plotting', language)
        if language == language_name:
            plot_language_mccs(language, new_figure = False, 
                prepend_label = 'clf ',
                offset = offset, color = colors[i], plot_grid = False)
        else:
            other_language_name = language
            print(language_name, other_language_name)
            results = filter_other_language(language_name, other_language_name)
            print(results)
            plot_language_mccs(language_name = other_language_name,
                results = results, 
                new_figure = False, error_alpha = .5, 
                offset = offset, color = colors[i], plot_grid = False)
        offset += delta_offset
    n_categories = len(classifier_order)
    _plot_vertical_lines(n_categories)
    plt.legend()
    plt.grid(alpha = .5, axis = 'y')
    

def matrix_cell(clf_language, data_language, layer_name = 'duration', 
    results = None):
    if not results: results = load_results(return_stats = True)
    if data_language == clf_language: 
        identifier = f'{clf_language}-{layer_name}'
    else:
        identifier=f'{clf_language}-{layer_name}-other-language-{data_language}'
    for result in results:
        if result['identifier'] == identifier:
            print(identifier, round(result['mean'],5))
            return result['mean']
    return 0
        

def mcc_matrix(layer_name = 'duration', plot = False):
    languages = language_names
    n_languages = len(languages)
    columns, rows = languages,languages 
    results = load_results()
    matrix = np.zeros((n_languages, n_languages))
    for i,data_language in enumerate(rows):
        for j,clf_language in enumerate(columns):
            matrix[i,j] = matrix_cell(clf_language, data_language, layer_name, 
                results)
    if plot: plot_matrix(matrix, columns, rows, ylabel = 'Data language',
        xlabel = 'Classifier language')
    return matrix

def plot_matrix(matrix, columns, rows, ylabel = '', xlabel = ''):
    plt.figure()
    plt.imshow(matrix, cmap = 'viridis')
    plt.xticks(np.arange(len(columns)), columns, rotation = 90)
    plt.yticks(np.arange(len(rows)), rows)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.colorbar()
    plt.tight_layout()
        
