from audio import audio
import json
import librosa
import numpy as np
from progressbar import progressbar
from utils import select
from utils import plot_distributions

def signal_to_pitch(signal, sr):
    f0 = librosa.yin(signal, fmin = 65, fmax=600, sr=sr)
    return [round(x) for x in f0]

def handle_phoneme(phoneme, signal, sr, save = True):
    '''compute the pitch of a phoneme object'''
    signal = audio.item_to_samples(phoneme, signal, sr)
    f0 = signal_to_pitch(signal, sr)
    phoneme._f0 = json.dumps(f0)
    if save: phoneme.save()
    return f0

def handle_word(word, signal, sr, save = True):
    '''compute the pitch of a word object'''
    phonemes = word.phoneme_set.all()
    pitches = []
    for phoneme in phonemes:
        f0 = handle_phoneme(phoneme, signal, sr)
        pitches.append(f0)
    return pitches

def handle_audio(audio):
    '''compute the pitch of all phonemes in an audio object'''
    signal, sr = audio.load_audio()
    words = audio.word_set.all()
    pitches = []
    for word in progressbar(words):
        o = handle_word(word, signal, sr)
        pitches.append(o)
    return pitches

def _to_pitch(frequency_list):
    n = len(frequency_list)
    if n == 0: return None
    if n < 4: return np.mean(frequency_list)
    if n <= 7: return np.mean(frequency_list[1:-1])
    if n <= 14: return np.mean(frequency_list[2:-2])
    return np.mean(frequency_list[3:-3])


def _vowels_to_pitch(vowel_stress_dict):
    d = vowel_stress_dict
    output = {}
    for k,v in d.items():
        output[k] = []
        for x in v:
            pitch = _to_pitch(x.f0)
            if not pitch: continue
            output[k].append(pitch)
    return output

def make_vowel_pitch_stress_dict(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''make dict mapping stress / no_stress to vowel durations'''
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    d = _vowels_to_pitch(d)
    return d

def plot_stress_no_stress_distributions(pitch = None, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 90, plot_density = False, xlabel = 'pitch (Hz)'):
    if not pitch: pitch = make_vowel_pitch_stress_dict()
    kwargs = {
        'value_dict':pitch,
        'new_figure':new_figure,
        'minimal_frame':minimal_frame,
        'ylim':ylim,
        'add_left':add_left,
        'add_legend':add_legend,
        'bins':bins,
        'xlabel':xlabel,
        'xlim':(50, 500),
        'plot_density':plot_density,
        }
    plot_distributions.plot_stress_no_stress_distributions(**kwargs)
