from audio import duration
from audio import formants
from audio import frequency_band
from audio import intensity
from audio import pitch
from audio import combined_features
from utils import select

from matplotlib import pyplot as plt
import numpy as np
import pickle
from scipy.stats import gaussian_kde


# circular imports for duration formants frequency_band intensity pitch
# not sure if this is a major issue

def _plot_density(data, label, color, alpha = 1, bins = 1000):
    kde = gaussian_kde(data)
    x = np.linspace(min(data), max(data), bins)
    y = kde(x)
    plt.plot(x, y, label = label, color = color, alpha = alpha)
    plt.fill_between(x, y, color = color, alpha = alpha/2)
    return max(y)
   

def plot_stress_no_stress_distributions(value_dict, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = '', xlim = None, plot_density = False):
    '''plot the stress and no stress distributions of a given value_dict
    dict should contain stress no_stress keys with lists of values 
    (e.g. duration)
    '''
    d = value_dict
    plt.ion()
    if new_figure: plt.figure()
    if plot_density: minimal_frame, add_left = True, False 
    ax = plt.gca()
    if minimal_frame:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    if ylim: plt.ylim(ylim)
    if xlim: plt.xlim(xlim)
    if plot_density:
        y1=_plot_density(d['stress'], 'stress', 'black', alpha = 1, bins = bins)
        y2=_plot_density(d['no_stress'], 'no stress', 'orange', alpha = .7, 
            bins = bins)
        y = max(y1,y2)
        plt.ylim((0,y))
        print(y1,y2,y)
    else:
        plt.hist(d['stress'], bins=bins, color = 'black', alpha=1,
            label='stress')
        plt.hist(d['no_stress'], bins=bins, color = 'orange', alpha=.7,
            label='no stress')
    if add_legend: plt.legend()
    plt.xlabel(xlabel)
    if add_left: plt.ylabel('Counts')
    else:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left = False)
        ax.set_yticklabels([])
    plt.grid(alpha=0.3, axis = 'x')

def get_all_data(language_name = 'dutch', dataset_name = 'COMMON VOICE',
    minimum_n_syllables = None, number_of_syllables = None, 
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    print('Processing durations')
    durations = duration.make_vowel_duration_stress_dict(vowel_stress_dict = d)
    print('Processing formants')
    formant = formants.make_vowel_f1f2_distance_stress_dict(vowel_stress_dict=d)
    print('Processing spectral tilt')
    X,y = frequency_band.make_dataset(vowel_stress_dict = d)
    clf, _, _ = frequency_band.train_lda(X, y, report = False)
    spectral_tilt = {'X':X, 'y':y, 'clf':clf}
    print('Processing intensities')
    intensities=intensity.make_vowel_intensity_stress_dict(vowel_stress_dict=d)
    print('Processing pitch')
    pitch_values = pitch.make_vowel_pitch_stress_dict(vowel_stress_dict=d)
    print('Processing combined')
    X, y = combined_features.make_dataset(vowel_stress_dict = d)
    clf, _, _ = combined_features.train_lda(X, y, report = False)
    combined_values = {'X':X, 'y':y, 'clf':clf}
    data = {
        'durations': durations,
        'formants': formant,
        'spectral_tilt': spectral_tilt,
        'intensities': intensities,
        'pitch': pitch_values,
        'combined': combined_values,
        }
    return data

def plot_all_acoustic_features(language_name = 'dutch',
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None, 
    ylim = (0,50_000), data = None, row_index = 1, nrows = 1, 
    new_figure = True, plot_density = False, grid = None,
    row_name = ''):
    '''plot all acoustic features'''
    if not data:
        data = get_all_data(language_name, dataset_name, minimum_n_syllables,
            max_n_items_per_speaker, vowel_stress_dict)
    plt.ion()
    if new_figure: plt.figure()
    if plot_density: 
        ylim, add_left = None,False
    else: add_left = True
    if nrows > 1 and row_index != nrows:kwargs = {'xlabel': ''}
    else: kwargs = {}
        
    plot_index = row_index * 6 - 6
    print('plot index', plot_index)
    plt.subplot(nrows,6,plot_index + 1)
    intensity.plot_stress_no_stress_distributions(data['intensities'],
        new_figure = False, minimal_frame = True, **kwargs,
        add_legend = False, ylim = ylim, plot_density = plot_density)
    if row_name: plt.title(row_name)
    plt.subplot(nrows,6,plot_index +2)
    duration.plot_stress_no_stress_distributions(data['durations'],
        new_figure = False, minimal_frame = True, plot_density = plot_density,
        add_left = False, add_legend = False, ylim = ylim, **kwargs )
    plt.subplot(nrows,6,plot_index + 3)
    formants.plot_stress_no_stress_distributions(data['formants'],
        new_figure = False, minimal_frame = True, plot_density = plot_density,
        add_left = False, add_legend = False, ylim = ylim, **kwargs )
    plt.subplot(nrows,6,plot_index + 4)
    pitch.plot_stress_no_stress_distributions(data['pitch'],
        new_figure = False, minimal_frame = True, plot_density = plot_density,
        add_left = False, add_legend = False, ylim = ylim, **kwargs )
    plt.subplot(nrows,6,plot_index + 5)
    frequency_band.plot_lda_hist(**data['spectral_tilt'],
        new_figure = False, minimal_frame = True, plot_density = plot_density,
        add_left = False, add_legend = False, ylim = ylim, **kwargs)
    plt.subplot(nrows,6,plot_index + 6)
    add_legend = True if row_index == nrows else False
    combined_features.plot_lda_hist(**data['combined'],
        new_figure = False, minimal_frame = True, plot_density = plot_density,
        add_left = False, add_legend = add_legend, ylim = ylim, **kwargs)
    return data

    
def plot_languages(language_names = ['dutch','german', 'english'],
    all_data = None, minimum_n_syllables = 1, max_n_items_per_speaker = None,
    plot_density = True):
    if not all_data:
        all_data = {}
        for language_name in language_names:
            all_data[language_name] = None
    nrows = len(all_data.keys())
    row_index = 1
    for language, data in all_data.items():
        print('Plotting', language, nrows, row_index)
        if row_index == 0: new_figure = True
        else: new_figure = False
        o = plot_all_acoustic_features(language_name = language,
            data = data, minimum_n_syllables = minimum_n_syllables,
            max_n_items_per_speaker = max_n_items_per_speaker, 
            nrows = nrows, row_index = row_index, 
            row_name = language.capitalize(),
            new_figure = new_figure,plot_density = plot_density)
        row_index += 1
        if not data:
            'storing data'
            all_data[language] = o
    return all_data

def save_all_data_dutch_german_english(all_data, filename = ''):
    if not filename:
        filename = '../data/acoustic_correlates'
        filename += '_dutch-german-english_n-sylalbles-2.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(all_data, f)
    
def load_all_data_dutch_german_english(filename = ''):
    if not filename:
        filename = '../data/acoustic_correlates'
        filename += '_dutch-german-english_n-sylalbles-2.pickle'
    with open(filename, 'rb') as f:
        all_data = pickle.load(f)
    return all_data
    
def make_all_data_dutch_german_english(save = False):
    all_data = {}
    for language_name in ['dutch','german','english']:
        print('Processing', language_name)
        all_data[language_name] = get_all_data(language_name, 
            number_of_syllables = 2)
    if save: save_all_data_dutch_german_english()
    return all_data
    
    
    
