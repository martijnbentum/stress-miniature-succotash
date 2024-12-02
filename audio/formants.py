import json
from utils import locations
from utils import plot_distributions
from utils import select
from matplotlib import pyplot as plt
import numpy as np
import os
from pathlib import Path
from progressbar import progressbar
import random
import string
import sys

# plot distance to the mean of f1 f2 for all vowels

def _reduce_frequency_list(frequency_list):
    '''reduce frequency list to a single value
    the frequencies are generated over the time course of a vowel
    the frequencies at the beginning and end of a vowel
    are less reliable, if the vowel is long they are removed
    '''
    n = len(frequency_list)
    if n == 0: return None
    if n < 4: return np.mean(frequency_list)
    if n <= 7: return np.mean(frequency_list[1:-1])
    if n <= 14: return np.mean(frequency_list[2:-2])
    return np.mean(frequency_list[3:-3])

def _to_f1f2(f1, f2):
    '''reduce formant values to a single value for both f1 and f2'''
    f1 = _reduce_frequency_list(f1)
    f2 = _reduce_frequency_list(f2)
    if not f1 or not f2: return None
    return f1, f2

def _vowels_to_f1f2(vowel_stress_dict):
    '''compute the f1 and f2 values for all vowels in a vowel_stress_dict
    the vowels have f1 and f2 values over time, these are reduced to a single
    value for f1 and a single value for f2
    '''
    d = vowel_stress_dict
    output = {}
    for k,v in d.items():
        output[k] = []
        for x in v:
            f1f2= _to_f1f2(x.f1, x.f2)
            if not f1f2: continue
            output[k].append(f1f2)
    return output

def make_vowel_f1f2_stress_dict(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''make dict mapping stress / no_stress to vowel f1 and f2 values'''
    if not vowel_stress_dict:
        assert type(language_name) == type(dataset_name) == str 
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    d = _vowels_to_f1f2(d)
    return d

def make_dataset(vowel_stress_dict): 
    d = _vowels_to_f1f2(vowel_stress_dict)
    X, y = [], []
    for stress_status,f1f2s in d.items():
        y_value = 1 if stress_status == 'stress' else 0
        for f1f2 in f1f2s:
            X.append(f1f2) 
            y.append(y_value)
    return X, y

def formant_dataset_to_distance_dataset(X):
    f1, f2 = X[:,0], X[:,1]
    global_f1, global_f2 = np.mean(X, axis = 0)
    return np.sqrt((f1 - global_f1)**2 + (f2 - global_f2)**2)
    


def global_f1f2(f1f2):
    '''uses the output of make_vowel_f1f2_stress_dict to make 
    global f1 f2 values
    '''
    f1, f2 = [], []
    for values in f1f2.values():
        for value in values:
            f1.append(value[0])
            f2.append(value[1])
    return f1, f2
            
def global_mean_f1f2(f1f2):
    '''compute the global mean f1 and f2 values for a f1f2 dict created with
    make_vowel_f1f2_stress_dict
    '''
    f1, f2 = global_f1f2(f1f2)
    return np.mean(f1), np.mean(f2)

def _compute_distance_to_global_mean(f1, f2, global_f1, global_f2):
    '''compute the distance of a f1 f2 value to the global mean f1 f2 value
    '''
    return np.sqrt((f1 - global_f1)**2 + (f2 - global_f2)**2)

def f1f2_to_f1f2_distance(f1f2):
    '''compute the distance of all f1 f2 values to the global mean f1 f2 values
    f1f2 is a dict created with make_vowel_f1f2_stress_dict
    '''
    global_f1, global_f2 = global_mean_f1f2(f1f2)
    output = {}
    for key, values in f1f2.items():
        output[key] = []
        for value in values:
            f1, f2 = value
            distance = _compute_distance_to_global_mean(f1, f2, 
                global_f1, global_f2)
            output[key].append(distance)
    return output

def make_vowel_f1f2_distance_stress_dict(language_name = 'dutch',
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''make dict mapping stress / no_stress to vowel f1 f2 distance 
    to global mean
    '''
    f1f2 = make_vowel_f1f2_stress_dict(language_name, dataset_name,
        minimum_n_syllables, max_n_items_per_speaker, vowel_stress_dict)
    f1f2_distance = f1f2_to_f1f2_distance(f1f2)
    return f1f2_distance

def plot_stress_no_stress_distributions(f1f2_distance = None, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 90, plot_density = False, xlabel = 'Formants (Hz)'):
    '''plot the distribution of f1 f2 distances for stress and no stress vowels.
    '''
    if not f1f2_distance: f1f2_distance= make_vowel_f1f2_distance_stress_dict()
    kwargs = {
        'value_dict':f1f2_distance,
        'new_figure':new_figure,
        'minimal_frame':minimal_frame,
        'ylim':ylim,
        'add_left':add_left,
        'add_legend':add_legend,
        'bins':bins,
        'xlabel':xlabel,
        'xlim':(0, 1500),
        'plot_density':plot_density,
        }
    plot_distributions.plot_stress_no_stress_distributions(**kwargs)

# plot vowel space

def _per_vowel_stress_mean_f1_f2(d):
    '''compute mean f1 and mean f2 for each vowel and stress status.
    '''
    for vowel in d.keys():
        for stress_status in d[vowel].keys():
            f1,f2=d[vowel][stress_status]['f1'],d[vowel][stress_status]['f2']
            d[vowel][stress_status]['f1_mean'] = np.mean(f1) 
            d[vowel][stress_status]['f2_mean'] = np.mean(f2) 


def _compute_vowel_overall_mean(d):
    '''helper function to compute mean f1 f2 for a vowel
    independent of stress status
    '''
    for vowel in d.keys():
        f1, f2 = [], []
        for stress_status in d[vowel].keys():
            f1.append(d[vowel][stress_status]['f1_mean'])
            f2.append(d[vowel][stress_status]['f2_mean'])
        d[vowel]['f1'] = np.mean(f1)
        d[vowel]['f2'] = np.mean(f2)

def _global_mean_vowel_space(d):
    '''compute global mean f1 and f2 values for a dict created with
    per_vowel_f1_f2_dict
    '''
    f1, f2 = [], []
    for vowel in d.keys():
        f1.append(d[vowel]['f1'])
        f2.append(d[vowel]['f2'])
    return np.mean(f1), np.mean(f2), f1, f2


def per_vowel_f1_f2_stress_dict(vowel_stress_dict, add_mean = True):
    '''create dictionary that maps vowel and stress status to f1 and f2 values.
    used to plot vowel space
    '''
    d = {}
    for stress_status, values in vowel_stress_dict.items():
        for vowel in values:
            if vowel.ipa not in d.keys(): d[vowel.ipa] = {}
            if stress_status not in d[vowel.ipa].keys():
                d[vowel.ipa][stress_status] = {'f1':[], 'f2':[]}
            f1f2 = _to_f1f2(vowel.f1, vowel.f2)
            if not f1f2: continue
            f1, f2 = f1f2
            d[vowel.ipa][stress_status]['f1'].append(f1)
            d[vowel.ipa][stress_status]['f2'].append(f2)
    if add_mean:    
        _per_vowel_stress_mean_f1_f2(d)
        _compute_vowel_overall_mean(d)
    return d


def plot_formants(vowel_stress_dict = None, d = None):
    '''plot vowel space with stress status
    d is a dict created with per_vowel_f1_f2_stress_dict
    '''
    if not d:
        d = per_vowel_f1_f2_dict(vowel_stress_dict, return_mean = True)
    plt.figure()
    plt.ion()
    plt.xlim(2300, 1050)
    plt.ylim(720, 330)
    mean_f1, mean_f2, f1, f2 = _global_mean_vowel_space(d)

    plt.scatter(f2, f1,color = 'lightgrey', marker= '.', label = 'vowel mean')
    for vowel,values in d.items():
        vowel_f1, vowel_f2 = d[vowel]['f1'], d[vowel]['f2']
        plt.text(vowel_f1+7.5, vowel_f2-4, vowel,
            color = 'lightgrey', fontsize = 16)
        for stress in values.keys():
            if stress not in ['stress', 'no_stress']: continue
            if vowel == 'ɪ': label =stress
            else: label = None
            color = 'black' if stress == 'stress' else 'orange'
            sf1 = d[vowel][stress]['f1_mean']
            sf2 = d[vowel][stress]['f2_mean']
            plt.scatter(sf2, sf1, marker = '.',color = color, label = label)
            plt.text(sf2+7.5, sf1-4, vowel, color = color, fontsize = 16)
    plt.scatter(mean_f2, mean_f1, marker = 'x', color = 'red',
        label = 'global mean')
    plt.grid(alpha = 0.3)
    plt.legend()
    plt.xlabel('F2')
    plt.ylabel('F1')
    plt.show()



def handle_audio(audio):
    formants = Formants(audio)
    words = audio.word_set.all()
    for word in progressbar(words):
        handle_word(word, formants)

def handle_word(word, formants, save = True):
    phonemes = word.phoneme_set.all()
    for phoneme in phonemes:
        handle_phoneme(phoneme, formants, save)

def handle_phoneme(phoneme, formants, save = True):
    f1, f2 = formants.f1_f2(phoneme)
    phoneme._f1 = json.dumps(f1)
    phoneme._f2 = json.dumps(f2)
    if save: phoneme.save()

class Formants:
    '''class to handle formant values for an audio file
    formant values are stored in a table file
    the formant values are computed with Praat
    '''
    def __init__(self, audio):
        self.audio = audio 
        self.table, self.header = load_formants(audio)
        self._make_formant_lines()

    def _make_formant_lines(self):
        self.formant_lines = [Formant_line(x) for x in self.table]

    def interval(self, start, end):
        lines = self.formant_lines
        lines = [x for x in lines if x.time >= start and x.time <= end]
        return lines

    def interval_mean_f1_f2(self, start, end):
        lines = self.interval(start, end)
        f1 = round(sum([x.f1 for x in lines if x.f1]) / len(lines))
        f2 = round(sum([x.f2 for x in lines if x.f2]) / len(lines))
        return f1, f2

    def mean_f1_f2(self, item):
        '''return mean f1 and f2 for item, typically a phoneme object
        phoneme object is defined in word.py
        '''
        start, end = item.start_time, item.end_time
        return self.interval_mean_f1_f2(start, end)

    def f1_f2(self, item):
        '''return all f1 and f2 values for item, typically a phoneme object
        phoneme object is defined in word.py
        '''
        start, end = item.start_time, item.end_time
        lines = self.interval(start, end)
        f1 = [round(x.f1) for x in lines if x.f1]
        f2 = [round(x.f2) for x in lines if x.f2]
        return f1, f2

            


class Formant_line:
    '''line from formant table with time and formant values'''
    def __init__(self, line):
        self.line = line
        self.time = float(line[0])
        self.nformants = int(line[1])
        try: self.f1 = float(line[2])
        except ValueError: self.f1 = None
        try: self.f2 = float(line[4])
        except ValueError: self.f2 = None

    def __repr__(self):
        return 'Time: {}, F1: {}, F2: {})'.format(self.time, self.f1, self.f2)


def load_formants(audio):
    '''load table file with formant values for word
    word is a word object defined in word.py
    '''
    filename = audio_to_formant_filename(audio)
    with open(filename, 'r') as f:
        temp= [x.split('\t') for x in f.read().split('\n') if x]
    header, table = temp[0], temp[1:]
    return table, header


def praat_script_filename():
    name = ''.join(random.sample(string.ascii_lowercase*10,30))
    filename = '../praat/' + name + '.praat'
    return filename

def handle_audio(audio):
    cmd = audio_praat_cmd(audio)
    filename_praat_script = praat_script_filename()
    with open(filename_praat_script, 'w') as fout:
        fout.write(cmd)
    if sys.platform == 'darwin':
        m = '/Applications/Praat.app/Contents/MacOS/Praat'
    else:
        m = 'praat'
    m += ' --run ' + filename_praat_script
    print(m)
    os.system(m)
    os.remove(filename_praat_script)

    

def audio_to_formant_filename(audio):
    formant_directory = locations.formants_dir.resolve()
    name = Path(audio.filename).stem + '.formants'
    filename = formant_directory / name
    return filename

def audio_praat_cmd(audio):
    formant_filename = audio_to_formant_filename(audio)
    audio_filename = Path(audio.filename).resolve()
    name = audio_filename.stem
    cmd = []
    cmd.append('Read from file: "{}"'.format(audio_filename))
    cmd.append('To Formant (burg): 0, 5, 5500, 0.025, 50')
    cmd.append('Down to Table: "no", "yes", 6, "no", 3, "yes", 3, "yes"')
    cmd.append('Save as tab-separated file: "{}"'.format(formant_filename))
    cmd.append('selectObject: "Sound {}"'.format(name))
    cmd.append('plusObject: "Formant {}"'.format(name))
    cmd.append('plusObject: "Table {}"'.format(name))
    cmd.append('Remove')
    return '\n'.join(cmd)
