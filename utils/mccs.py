import json
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from utils import stats

language_names = ['dutch', 'english', 'german', 'polish', 'hungarian']
classifier_order = ['duration', 'intensity', 'pitch', 'formant',
    'spectral-tilt', 'combined-features', 'codevector', 'cnn', 5, 11, 
    17, 23]
        
def load_results(return_stats = True, focus_language = None, 
    filename = '../results.json'):
    with open(filename) as f:
        d = json.load(f)
    for result in d:
        result['identifier'] = _result_to_identifier(result)
    if return_stats: return results_to_stats(d, focus_language = focus_language)
    return d

def _result_to_identifier(result):
    language_name = result['language_name']
    layer = result['layer']
    name = result['name']
    n = result['n']
    if name: return f'{language_name}-{layer}-{name}'
    if n: return f'{language_name}-{layer}-{n}'
    return f'{language_name}-{layer}'

def results_to_stats(results, focus_language = None):
    output = {}
    for result in results:
        identifier = _result_to_identifier(result)
        language_name = result['language_name']
        if focus_language:  
            if language_name != focus_language: continue
            if not 'other-language-' in identifier: continue
            identifier = identifier.split('-other')[0] + '-other-language-'
            print(identifier)
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

def filter_cross_lingual(results = None, cross_lingual = True):
    if not results: results = load_results()
    output = []
    if cross_lingual:
        print('loading cross-lingual results')
    else:
        print('loading monolingual results')
    for result in results:
        if cross_lingual:
            if 'other-language-' in result['name']:
                output.append(result)
        else:
            if not 'other-language-' in result['name']:
                output.append(result)
    return output

def filter_language(language_name, cross_lingual = False, finetuned = False,
    focus_language = None):
    if focus_language: 
        print('loading with focus language', focus_language)
        results = load_results(focus_language = language_name)
    else:
        results = filter_cross_lingual(cross_lingual = cross_lingual)
    output = []
    for result in results:
        if language_name == result['language_name']:
            if finetuned:
                if 'finetuned' in result['identifier']:
                    output.append(result)
            else:
                if not 'finetuned' in result['identifier']:
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
    error_alpha = 1, prepend_label = '', append_label = '', finetuned = False, 
    focus_language = None):
    if not results: results = filter_language(language_name, 
        finetuned = finetuned, focus_language = focus_language) 
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    x_temp = np.arange(len(classifier_order)) + offset
    temp = [result['layer'] for result in results]
    x, x_tick_names = [], []
    for i, co in enumerate(classifier_order):
        if co in temp:
            x.append(x_temp[i])
            x_tick_names.append(co)
    # x_tick_names = [co for co in classifier_order if co in temp]
    if 'combined-features' in x_tick_names: 
        x_tick_names[x_tick_names.index('combined-features')] = 'combined'
    print(x,x_tick_names)
    means = [result['mean'] for result in results]
    cis = [result['ci'] for result in results]
    plt.errorbar(x, means, yerr = cis, 
        label = prepend_label + language_name + append_label, 
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
    legend = plt.legend()
    texts = legend.get_texts()
    for text in texts:
        if 'clf' in text.get_text(): text.set_color('red') 
    plt.grid(alpha = .5, axis = 'y')

def compare_pretrained_finetuned_other(language_name = 'dutch', 
    new_figure = True):
    plot_language_mccs(language_name, new_figure = True)
    plot_language_mccs(language_name, new_figure = False, finetuned = True,
        color = 'red', plot_grid = False, prepend_label = 'finetuned ',
        error_alpha = .8)
    plot_language_mccs(language_name, new_figure = False,
        focus_language = language_name,
        color = 'grey', plot_grid = False, 
        append_label = ' tested on other languages', error_alpha = 0.6)
    plt.legend()
        

    

def matrix_cell(clf_language, data_language, layer_name = 'duration', 
    results = None, stats = True, allow_empty = False):
    if not results: results = load_results(return_stats = stats)
    if data_language == clf_language: 
        identifier = f'{clf_language}-{layer_name}'
    else:
        identifier=f'{clf_language}-{layer_name}-other-language-{data_language}'
    o = []
    print(identifier)
    random_states = []
    for result in results:
        if not stats:
            random_state = result['random_state']
            if random_state == 42: continue
        if result['identifier'] == identifier:
            if stats:
                print(identifier, round(result['mean'],5))
                return result['mean']
            elif random_state not in random_states:
                o.append(result['mcc'])
                random_states.append(random_state)
    if not stats: 
        if not o: 
            if allow_empty: return np.zeros(20)
        return np.array(o)
    return 0
        

def mcc_matrix(layer_name = 'duration', plot = False, stats = False,
    result_filename = '../results.json', allow_empty = False):
    languages = language_names
    n_languages = len(languages)
    columns, rows = languages,languages 
    results = load_results(return_stats = stats, filename = result_filename)
    if stats:
        matrix = np.zeros((n_languages, n_languages))
    else:
        matrix = np.zeros((n_languages * 20, n_languages))
        y = np.zeros(n_languages * 20, dtype = int)
    for i,clf_language in enumerate(rows):
        for j,data_language in enumerate(columns):
            if stats: 
                start = i
                end = i + 1
            else:
                start = i * 20
                end = i * 20 + 20
            matrix[start:end,j] = matrix_cell(clf_language, data_language, 
                layer_name, 
                results, stats, allow_empty = allow_empty)
        if not stats: y[start:end] = i
    if plot: plot_matrix(matrix, columns, rows, xlabel = 'Data language',
        ylabel = 'Classifier language')
    if stats:
        return matrix
    return matrix, y

def plot_matrix(matrix, columns, rows, ylabel = '', xlabel = ''):
    plt.figure()
    plt.imshow(matrix, cmap = 'viridis')
    plt.xticks(np.arange(len(columns)), columns, rotation = 90)
    plt.yticks(np.arange(len(rows)), rows)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.colorbar()
    plt.tight_layout()
        

def scatter_plot_lda(layer_name = 17, add_legend = True, add_sup_title = True,
    new_figure = True, ax = None, add_axis_labels = True, 
    result_filename = '../results.json'):
    plt.ion()
    if new_figure:
        plt.figure()
    lda = LinearDiscriminantAnalysis(n_components=2)
    colors = ['red', 'green', 'blue','purple','orange']
    X, y = mcc_matrix(layer_name,stats = False, 
        result_filename = result_filename)
    X_lda = lda.fit_transform(X, y)
    if ax: p = ax
    else: p = plt
    for color, i, language_name in zip(colors, np.unique(y), language_names):
        p.scatter(X_lda[y == i, 0], X_lda[y == i, 1], alpha = .6, c = color,
            label = language_name)
    if add_sup_title:
        p.suptitle('LDA of cross lingual classifier performance output')
    if ax:
        if layer_name == 'combined-features': layer_name = 'combined'
        p.set_title(f'Layer: {layer_name}')
    else: plt.title(f'Layer: {layer_name}')
    if add_axis_labels:
        if ax:
            p.set_xlabel('LD1', labelpad = -5)
            p.set_ylabel('LD2')
        else:
            p.xlabel('LD1')
            p.ylabel('LD2')
    if add_legend:
        p.legend()
    p.grid(alpha = .5)

def scatter_plot_lda_all_classifiers():
    fig, axs = plt.subplots(4, 3)
    axes = list(axs.flat)
    for i,layer_name in enumerate(classifier_order):
        add_legend = False
        add_axis_labels = False
        if i == 0: 
            add_legend = True
            # add_axis_labels = True
        scatter_plot_lda(layer_name, add_legend = add_legend,
            add_sup_title = False, new_figure = False, 
            add_axis_labels = add_axis_labels, ax = axes[i])
