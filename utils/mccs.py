from audio import duration
from audio import formants
from audio import intensity
from audio import pitch
from audio import combined_features
from audio import frequency_band
import json
from matplotlib import pyplot as plt
import numpy as np
import os
from pathlib import Path
from progressbar import progressbar
from utils import density_classifier
from utils import lda, perceptron
from utils import select
from utils.results import Results, to_mccs, _to_mcc_dict
from utils import stats

def _check_cf_data(data, vowel_stress_dict):
    if vowel_stress_dict is None:
        X, y = data
        if len(X) == 0:
            print('no vowel_stress_dict and no data')
            return False
        return True
    if 'stress' in vowel_stress_dict.keys():
        stress = vowel_stress_dict['stress']
        if len(stress) == 0:
            print('no stressed vowels')
            return False
        return True
    return False

def _fix_all_combined_features(overwrite = False):
    from text.models import Language
    output = {}
    for language in Language.objects.all():
        print('handling', language.language)
        language_name = language.language.lower()
        filename=f'../results/{language_name}_combined_features_fix.json'
        if os.path.exists(filename) and not overwrite: 
            print(filename, 'already exists, skipping')
            continue
        data = combined_features.load_dataset(language_name)
        if not data: 
            _, vowel_stress_dict = handle_language(
                language_name = language_name, 
                save = False, do_mccs_computations = False)
        else: vowel_stress_dict = None
        data_ok = _check_cf_data(data, vowel_stress_dict)
        if not data_ok:
            print('data not ok', language_name)
            continue
        mccs = _fix_combined_features_mccs(language = language_name, 
            vowel_stress_dict = vowel_stress_dict, combined_feature = data)
        save_dict_to_json(mccs, filename)
        output[language_name] = mccs
    return output

def _fix_combined_features_mccs(language = 'dutch', combined_feature = None,
    vowel_stress_dict = None, n = 20):
    '''combined features did not use duration and did not use mlp
    this will recomputes the mccs for combined features
    '''
    if not combined_feature:
        print('making combined features dataset')
        combined_feature = combined_features.make_dataset(
            vowel_stress_dict = vowel_stress_dict)
        X, y = combined_feature
        combined_features.save_dataset(language.lower(), X, y)
    mccs = []
    for i in progressbar(range(n)):
        clf, data, report = make_combined_feature_classifier(
            combined_feature = combined_feature, random_state = i,)
        perceptron.save_classifier(clf, language.lower(), 'stress', 
        'combined-features', 
        'vowel', name = '',random_state = i)
        mccs.append(report['mcc'])
    return mccs
        

def handle_language(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = None, 
    number_of_syllables = 2, name = '',
    max_n_items_per_speaker = None, vowel_stress_dict = None, save = False,
    no_diphtongs = True, one_vowel_per_syllable = True, has_stress = True,
    do_mccs_computations = False):
    if not vowel_stress_dict:
        words = select.select_words(language_name = language_name,
            dataset_name = dataset_name, 
            minimum_n_syllables = minimum_n_syllables,
            number_of_syllables = number_of_syllables, 
            no_diphtongs = no_diphtongs, 
            one_vowel_per_syllable = one_vowel_per_syllable, 
            has_stress = has_stress)
        syllables = select.words_to_syllables(words)
        vowels = select.syllables_to_vowels(syllables)
        vowel_stress_dict = select.make_stress_dict(vowels)
    d = vowel_stress_dict
    if do_mccs_computations:
        mccs = compute_acoustic_correlates_mccs(n = 20, vowel_stress_dict = d)
    else: mccs = None
    if save:
        if name: name = f'_{name}'
        filename=f'../results/{language_name}_'
        filename+=f'vowel_mccs_clf_acoustic_correlates{name}.json'
        save_dict_to_json(mccs, filename)
    return mccs, vowel_stress_dict
    
def compute_acoustic_correlates_mccs(n = 20, formant_data = None, 
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
    return combined_features.train_perceptron(X, y,  
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

        
