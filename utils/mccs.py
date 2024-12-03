import json
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
from utils import stats

classifier_order = 'duration,intensity,pitch,formant,spectral-tilt'
classifier_order += ',combined-features,codevector,cnn,5,11,17,23'
classifier_order = classifier_order.split(',')

def load_results():
    with open('../results.json') as f:
        d = json.load(f)
    return d

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

        
