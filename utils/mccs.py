import json
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import numpy as np
from pathlib import Path
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from utils import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.patches as patches

language_names = ['dutch', 'english', 'german', 'polish', 'hungarian']
classifier_order = ['duration', 'intensity', 'pitch', 'formant',
    'spectral-tilt', 'combined-features', 'codevector', 'cnn', 5, 11, 
    17, 23]
co_short = ['dur', 'int', 'pit', 'for', 'st', 'cf', 'cv', 'cnn', 5, 11, 17, 23]
        
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

def _comput_stats(output):
    o = []
    for key, item in output.items():
        item['mean'], item['sem'], item['ci'] = stats.compute_mean_sem_ci(
            item['mccs'])
        item['mccs'] = [round(x, 3) for x in item['mccs']]
        item['identifier'] = key
        o.append(item)
    return o

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
    o = _comput_stats(output)
    return o 

def make_stats_language_specific_versus_other(results):
    output = {}
    for result in results:
        identifier = _result_to_identifier(result)
        if 'finetuned' in identifier: continue
        layer = result['layer']
        mcc = result['mcc']
        d = {'mccs': [mcc], 'layer': layer}
        if 'other-language-' in identifier:key = 'other-' + str(layer)
        else: key = 'specific-' + str(layer)
        if key not in output:
            output[key] = d
        else: output[key]['mccs'].append(mcc)
    o = _comput_stats(output)
    other = [x for x in o if 'other' in x['identifier']]
    other= sorted(other, key = lambda x: classifier_order.index(x['layer']))
    specific = [x for x in o if 'specific' in x['identifier']]
    specific= sorted(specific, key = lambda x: classifier_order.index(x['layer']))
    return specific, other
        

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
    focus_language = None, short_xlabels = False):
    if not results: results = filter_language(language_name, 
        finetuned = finetuned, focus_language = focus_language) 
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    x_temp = np.arange(len(classifier_order)) + offset
    temp = [result['layer'] for result in results]
    x, x_tick_names = [], []
    con = classifier_order if not short_xlabels else co_short
    for i, co in enumerate(con):
        if co in temp or short_xlabels:
            x.append(x_temp[i])
            x_tick_names.append(co)
    # x_tick_names = [co for co in classifier_order if co in temp]
    if 'combined-features' in x_tick_names: 
        x_tick_names[x_tick_names.index('combined-features')] = 'combined'
    print(x,x_tick_names)
    means = [result['mean'] for result in results]
    cis = [result['ci'] for result in results]
    language_name = language_name.capitalize()
    plt.errorbar(x, means, yerr = cis, 
        label = prepend_label + language_name + append_label, 
        markersize = 12,
        color = color, fmt = ',', elinewidth = 1.5, capsize = 3, 
        capthick = 1.5, alpha = error_alpha)
    if abs(x[0]) < 0.01:
        plt.xticks(x, x_tick_names, rotation = 90)
    plt.ylabel('MCC')
    if plot_grid: plt.grid(alpha = .5) 
    plt.tight_layout()

def _plot_vertical_lines(n_categories, width = 1):
    x = np.arange(n_categories)
    offset = width / 2
    for i in range(n_categories):
        if i % 2 == 0:
            plt.axvspan(x[i] - offset, x[i] + offset, color = 'grey', 
                alpha = .1) 
    
def plot_mccs(new_figure = True, languages= [], short_xlabels = False):
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
            offset = offset, color = colors[i], plot_grid = False,
            short_xlabels = short_xlabels)
        offset += delta_offset
    n_categories = len(classifier_order)
    _plot_vertical_lines(n_categories)
    plt.legend()
    plt.grid(alpha = .5, axis = 'y')

def plot_specific_versus_other(new_figure = True, 
    short_xlabels = False):
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    names = ['language specific', 'cross-lingual']
    n_names = len(names)
    results = load_results(False)
    specific, other = make_stats_language_specific_versus_other(results)
    results = [specific,  other]
    delta_offset = 1 / n_names
    offset = 0 - delta_offset 
    print('offset', offset)
    # colors = plt.get_cmap('tab10').colors
    colors = ['red', 'black']
    for i,name in enumerate(names):
        result = results[i]
        print('plotting', name)
        plot_language_mccs(name, new_figure = False, 
            offset = 0, color = colors[i], plot_grid = False,
            results = result, short_xlabels = short_xlabels)
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
    colors = plt.get_cmap('tab10').colors
    # colors = ['red', 'green', 'blue','purple','orange']
    X, y = mcc_matrix(layer_name,stats = False, 
        result_filename = result_filename)
    X_lda = lda.fit_transform(X, y)
    if ax: p = ax
    else: p = plt
    for color, i, language_name in zip(colors, np.unique(y), language_names):
        p.scatter(X_lda[y == i, 0], X_lda[y == i, 1], alpha = .6, c = color,
            label = language_name.capitalize())
    if add_sup_title:
        p.suptitle('LDA of cross lingual classifier performance output')
    if ax:
        if layer_name == 'combined-features': layer_name = 'combined'
        p.set_title(f'{layer_name}')
    else: plt.title(f'{layer_name}')
    if add_axis_labels:
        if ax:
            p.set_xlabel('LD1', labelpad = -5)
            p.set_ylabel('LD2')
        else:
            p.xlabel('LD1')
            p.ylabel('LD2')
    if add_legend:
        legend = p.legend(borderpad =0.1)
        for handle in legend.legendHandles:
            handle.set_alpha(1)
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

def ahc_dendrogram(layer = 11, result_filename = '../results.json', ax = None,
    ylim = (0,3), ylabel = 'Ward distance', show_legend = True, show = False,
        minimalist= False):
    X, y = mcc_matrix(layer,stats = False, 
        result_filename = result_filename)
    labels = y # [language_names[i][0] for i in y]
    Z = linkage(X, 'ward')
    if not ax:
        fig, ax = plt.subplots()
    plt.ion()
    dendro = dendrogram(Z, labels = labels, above_threshold_color = 'black',
        link_color_func = lambda x: 'black', ax = ax)
    leaf_order = dendro['leaves']
    x_labels = ax.get_xticklabels()
    colors = plt.get_cmap('tab10').colors
    mp = [mpatches.Patch(color =colors[i], label=language_names[i]) 
        for i in range(len(language_names))]
    height = (ylim[1] - ylim[0]) / 3 * -1
    for i, lbl in enumerate(x_labels):
        x_pos = lbl.get_position()[0]
        color = colors[y[leaf_order[i]]]
        rect = patches.Rectangle((x_pos - 2, 0 ), 9, height, 
            color=color, clip_on=False)
        ax.add_patch(rect)
        ax.set_xticks([])
    ax.set_title(f'{layer}')
    ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)
    if minimalist:
        ax.set_yticks([])
        ax.set_yticklabels([])
        [spine.set_visible(False) for spine in ax.spines.values()]
    if show_legend:
        ax.legend(handles = mp, labelspacing=0.3, framealpha = 1) 
    # plt.tight_layout()
    if show:
        plt.show()

def plot_ahc_dendrograms_article():
    layers = ['combined-features', 17]
    fig, axs = plt.subplots(1, 2, figsize = (12, 2))
    i = 0
    for ax, layer in zip(axs, layers):
        if i == 0: show_legend = True
        else: show_legend = False
        print(i)
        ahc_dendrogram(layer, ax = ax, ylim = (0,4), ylabel = '',
            show_legend = show_legend, show = False, minimalist = True)
        i += 1
    plt.tight_layout()
    plt.show()

