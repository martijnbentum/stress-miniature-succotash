from audio import combined_features 
from audio import duration 
from audio import formants
from audio import frequency_band
from audio import intensity
from audio import pitch 
import os
import pickle
from utils import select
from utils import locations

feature_names = ['spectral-tilt', 'combined-features', 'formant', 'intensity', 
    'pitch', 'duration']

language_names = ['dutch', 'english', 'spanish', 'german', 
    'polish', 'hungarian']

def check_datasets_language_exist(language_name, verbose = True):
    output = []
    for name in feature_names:
        exists = check_dataset_exists(language_name, name, verbose = False)
        output.append(exists)
        if verbose: print(f'{language_name} {name} exists: {exists}')
    if sum(output) == len(output):
        print(f'all datasets exist for {language_name}')
        return True
    return False

def check_datasets_all_languages_exist():
    for language_name in language_names:
        check_datasets_language_exist(language_name, False)

def handle_languages(overwrite = False):
    for language_name in language_names:
        handle_language(language_name, overwrite = overwrite)

def handle_language(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = None, 
    number_of_syllables = 2, no_diphtongs = True,one_vowel_per_syllable = True,
    has_stress = True, vowel_stress_dict = None, overwrite = False):
    if not overwrite and check_datasets_language_exist(language_name):
        print(f'all datasets exist for {language_name} doing nothing')
        return
    if not vowel_stress_dict:
        vowel_stress_dict = get_vowel_stress_dict(language_name, dataset_name, 
            minimum_n_syllables, number_of_syllables, no_diphtongs, 
            one_vowel_per_syllable, has_stress)
    for feature_name in feature_names:
        make_dataset(language_name, feature_name, vowel_stress_dict)
    

def get_vowel_stress_dict(language_name, dataset_name = 'COMMON VOICE', 
    minimum_n_syllables=None, number_of_syllables=2, no_diphtongs=True,
    one_vowel_per_syllable=True, has_stress=True):

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
    return vowel_stress_dict

def check_dataset_exists(language_name, feature_name, verbose = True):
    dataset_filename = make_dataset_filename(language_name, feature_name)
    if not os.path.exists(dataset_filename):
        if not verbose: return False
        print(f'file {dataset_filename} with feature: {feature_name}',
            'does not exist')
        return False
    return True

def make_dataset(language_name, feature_name, vowel_stress_dict, 
    overwrite = False):
    if not overwrite and check_dataset_exists(language_name, feature_name):
        print(f'dataset {feature_name} already exists for {language_name}')
        return load_dataset(language_name, feature_name)
    function = feature_name_to_dataset_dict[feature_name]
    print(f'making {feature_name} dataset for {language_name}')
    X, y = function(vowel_stress_dict = vowel_stress_dict)
    save_dataset(language_name, feature_name, X, y)
    return load_dataset(language_name, feature_name)

def save_dataset(language_name, feature_name, X, y):
    dataset_filename = make_dataset_filename(language_name, feature_name)
    print(f'saving {feature_name} dataset to {dataset_filename}')
    d = {'X':X,'y':y, 'language_name':language_name, 
        'layer':feature_name,'n':None, 'name':None, 'section':'vowel'}
    with open(dataset_filename, 'wb') as f:
        pickle.dump(d, f)

def load_dataset(language_name, feature_name):
    dataset_filename = make_dataset_filename(language_name, feature_name)
    print(f'loading {feature_name} features dataset from {dataset_filename}')
    if not check_dataset_exists(language_name, feature_name):
        return None
    with open(dataset_filename, 'rb') as f:
        d = pickle.load(f)
    return d['X'], d['y']

def make_dataset_filename(language_name, feature_name):
    language_name = language_name.lower()
    dataset_dir= locations.dataset_dir
    dataset_filename = f'{dataset_dir}/xy_dataset-stress_'
    dataset_filename += f'language-{language_name}_section-vowel_'
    dataset_filename += f'layer-{feature_name}_n-_name-.pickle'
    return dataset_filename

feature_name_to_dataset_dict = {
    'spectral-tilt':frequency_band.make_dataset,
    'combined-features':combined_features.make_dataset,
    'formant':formants.make_dataset,
    'intensity':intensity.make_dataset,
    'pitch':pitch.make_dataset,
    'duration':duration.make_dataset}
