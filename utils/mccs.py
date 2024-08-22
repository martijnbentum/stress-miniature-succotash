from audio import duration
from audio import formants
from audio import intensity
from audio import pitch
from audio import combined_features
from audio import frequency_band
import json
from matplotlib import pyplot as plt
import numpy as np
from progressbar import progressbar
from utils import density_classifier
from utils import lda
from utils import select
from utils.results import Results, to_mccs, _to_mcc_dict

def handle_language(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = None, 
    number_of_syllables = 2, name = '',
    max_n_items_per_speaker = None, vowel_stress_dict = None, save = True):
    if not vowel_stress_dict:
        d = select.select_vowels(
            language_name = language_name, 
            dataset_name = dataset_name,
            minimum_n_syllables = minimum_n_syllables, 
            max_n_items_per_speaker = max_n_items_per_speaker, 
            return_stress_dict = True, 
            number_of_syllables = number_of_syllables)
    else: d = vowel_stress_dict
    mccs = compute_acoustic_correlates_mccs(n = 30, vowel_stress_dict = d)
    if save:
        if name: name = f'_{name}'
        filename=f'../results/{language_name}_'
        filename+=f'vowel_mccs_clf_acoustic_correlates{name}.json'
        save_dict_to_json(mccs, filename)
    return mccs
    
def compute_acoustic_correlates_mccs(n = 30, formant_data = None, 
    intensities = None, pitches = None, durations = None, spectral_tilts = None, 
    combined_feature = None,vowel_stress_dict = None):
    mccs = {'spectral tilt':[], 'combined features':[], 'formant':[], 
        'intensity':[], 'pitch':[], 'duration':[]}
    for key in mccs.keys():
        if key == 'formant':
            data = formant_data
            function = make_formant_classifier
        if key == 'intensity':
            data = intensities
            function = make_intensity_classifier
        if key == 'pitch':
            data = pitches
            function = make_pitch_classifier
        if key == 'duration':
            data = durations
            function = make_duration_classifier
        if key == 'spectral tilt':
            data = spectral_tilts
            function = make_spectral_tilt_classifier
        if key == 'combined features':
            data = combined_feature
            function = make_combined_feature_classifier
        print('handling', key)
        for i in progressbar(range(n)):
            clf = function(data, random_state=i, 
                vowel_stress_dict = vowel_stress_dict)
            if key == 'spectral tilt' or key == 'combined features':
                mccs[key].append(clf[-1]['mcc'])
            else:
                _ = clf.classification_report()
                mccs[key].append(clf.mcc)
        print(key, 'done',np.mean(mccs[key]), np.std(mccs[key]), mccs[key])
    return mccs

def make_formant_classifier(stress_distance = None, random_state=42,
       vowel_stress_dict = None, verbose = False):
    if not stress_distance:
        if verbose:print('computing vowel formant distance to global mean')
        stress_distance = formants.make_vowel_f1f2_distance_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = stress_distance['stress']
    no_stress = stress_distance['no_stress']
    clf = density_classifier.Classifier(stress, no_stress, name = 'formant', 
        random_state=random_state)
    return clf
    
def make_intensity_classifier(intensities = None, random_state=42,
        vowel_stress_dict = None, verbose = False):
    if not intensities:
        if verbose:print('computing vowel intensities')
        intensities=intensity.make_vowel_intensity_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = intensities['stress']
    no_stress = intensities['no_stress']
    clf = density_classifier.Classifier(stress, no_stress, name = 'intensity', 
        random_state=random_state)
    return clf

def make_pitch_classifier(pitches = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not pitches: 
        if verbose:print('computing vowel pitch')
        pitches= pitch.make_vowel_pitch_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = pitches['stress']
    no_stress = pitches['no_stress']
    clf = density_classifier.Classifier(stress, no_stress, name = 'pitch', 
        random_state=random_state)
    return clf

def make_duration_classifier(durations = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not durations: 
        if verbose:print('computing vowel durations')
        durations = duration.make_vowel_duration_stress_dict(
            vowel_stress_dict = vowel_stress_dict)
    stress = durations['stress']
    no_stress = durations['no_stress']
    print('making classifier')
    clf = density_classifier.Classifier(stress, no_stress, name = 'duration', 
        random_state=random_state)
    return clf

def make_spectral_tilt_classifier(spectral_tilts = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not spectral_tilts: 
        if verbose: print('computing vowel spectral tilts')
        spectral_tilts = frequency_band.make_dataset(
            vowel_stress_dict = vowel_stress_dict)
    X, y = spectral_tilts
    return frequency_band.train_lda(X, y, report = True, 
        random_state = random_state)

def make_combined_feature_classifier(combined_feature = None, random_state=42,
    vowel_stress_dict = None, verbose = False):
    if not combined_feature: 
        if verbose: print('computing vowel combined feature')
        combined_feature = combined_features.make_dataset(
            vowel_stress_dict = vowel_stress_dict)
    X, y = combined_feature
    return combined_features.train_lda(X, y, report = True, 
        random_state = random_state)

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
    
def plot_mccs(mcc_result_dict = None, new_figure = True):
    if not mcc_result_dict:
        with open('../results/mccs_stress_vowel.json') as f:
            mcc_result_dict = json.load(f)
    plt.ion()
    if new_figure: plt.figure()
    plt.ylim(0,1)
    n_languages = len(mcc_result_dict.keys())
    delta_offset = 1 / n_languages
    offset = 0 - delta_offset
    colors = plt.get_cmap('tab10').colors
    for i,language in enumerate(mcc_result_dict.keys()):
        print('plotting', language)
        _plot_language_mccs(mcc_result_dict, language, new_figure = False, 
            offset = offset, color = colors[i])
        offset += delta_offset
    n_categories = len(mcc_result_dict[language].keys())
    _plot_vertical_lines(n_categories)
    plt.legend()
    plt.grid(alpha = .5, axis = 'y')

        
