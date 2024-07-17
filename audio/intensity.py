from audio import audio
import numpy as np
from utils import select
from utils import plot_distributions

def compute_praat_intensity(signal):
    '''
    compute the intensity of a signal using praat's intensity algorithm
    '''
    baseline = 4 * 10 ** -10
    power = np.mean(signal ** 2)
    return 10 * np.log10(power / baseline)

def handle_phoneme(phoneme, signal, sr, save = False):
    '''compute the intensity of a phoneme object'''
    signal = audio.item_to_samples(phoneme, signal, sr)
    intensity = compute_praat_intensity(signal)
    phoneme.intensity = round(intensity,3)
    if save: phoneme.save()
    return intensity

def handle_word(word, signal, save = False):
    '''compute the pitch of a word object'''
    phonemes = word.phoneme_set.all()
    intensities = []
    for phoneme in phonemes:
        intensity = handle_phoneme(phoneme, signal, sr, save = save)
        intensities.append(intensity)
    return intensities

def handle_audio(audio):
    '''compute the pitch of all phonemes in an audio object'''
    signal, sr = audio.load_audio()
    words = audio.word_set.all()
    intensities = []
    for word in words:
        o = handle_word(word, signal)
        intensities.append(o)
    return intensities

def _vowels_to_intensity(vowel_intensity_stress_dict):
    d = vowel_intensity_stress_dict
    if not d: d = make_vowel_duration_stress_dict('dutch')
    output = {}
    for k,v in d.items():
        output[k] = [x.intensity for x in v]
    return output

def make_vowel_intensity_stress_dict(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''make dict mapping stress / no_stress to vowel intensities'''
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker,
            return_stress_dict = True)
    else: d = vowel_stress_dict
    d = _vowels_to_intensity(d)
    return d

def plot_stress_no_stress_distributions(intensities = None, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 240):
    if not intensities: make_vowel_intensity_stress_dict()
    kwargs = {
        'value_dict':intensities,
        'new_figure':new_figure,
        'minimal_frame':minimal_frame,
        'ylim':ylim,
        'add_left':add_left,
        'add_legend':add_legend,
        'bins':bins,
        'xlabel':'Intensity (dB)',
        'xlim':(40,90),
        }
    plot_distributions.plot_stress_no_stress_distributions(**kwargs)


