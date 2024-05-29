from audio import audio
import numpy as np
from progressbar import progressbar

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
