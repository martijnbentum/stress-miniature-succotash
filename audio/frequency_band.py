from audio import audio
from utils import select
from utils import lda
import json
import librosa
import matplotlib.pyplot as plt
import numpy as np
from progressbar import progressbar

praat_baseline_power = 4*10**-10

def handle_phoneme(phoneme, signal, sr, baseline_power = None, save = True):
    '''compute the power in four frequency bands and convert to decibels
    for a specific vowel in a word.
    phoneme     phoneme class object 
    '''
    signal = audio.item_to_samples(phoneme, signal, sr)
    try:spectral_tilt = [round(x) for x in get_four_fb_to_db(signal, sr = sr)]
    except OverflowError: return ''
    if sum([x < 0 for x in spectral_tilt]) > 0: return ''
    phoneme._spectral_tilt = json.dumps(spectral_tilt)
    if save: phoneme.save()
    return spectral_tilt

def handle_word(word, signal, sr):
    '''compute the power in four frequency bands and convert to decibels
    '''
    phonemes = word.phoneme_set.all()
    spectral_tilts = []
    for phoneme in phonemes:
        spectral_tilt= handle_phoneme(phoneme, signal, sr)
        spectral_tilts.append(st)
    return spectral_tilts

def handle_audio(audio):
    '''compute the spectral tilt of all phonemes in an audio object'''
    signal, sr = audio.load_audio()
    words = audio.word_set.all()
    spectral_tilts = []
    for word in progressbar(words):
        o = handle_word(word, signal, sr)
        spectral_tilts.append(o)
    return spectral_tilts

def compute_fft(signal, sr = 44100):
    '''compute the fast fourier transform of a signal
    returns only the positive frequencies
    frequencies         a list of frequencies corresponding to the fft_result
    fft_result          a list of complex numbers -> fourier decomposition
                        of the signal
    '''
    fft_result= np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), 1.0/sr)
    frequencies = frequencies[:int(len(frequencies)/2)] 
    fft_result = fft_result[:int(len(fft_result)/2)]
    return frequencies, fft_result

def compute_power_spectrum(signal, sr = 44100):
    '''compute the power spectrum of a signal
    frequencies         a list of frequencies corresponding to the fft_result
    power_spectrum      a list of real numbers -> power of the signal at each
                        frequency in frequencies
    '''
    frequencies, fft_result = compute_fft(signal, sr)
    # the factor of 4 is to account for the fact that we only use the positive
    # frequencies
    power_spectrum = 10 * np.log10(4 * np.abs(fft_result)**2)
    return frequencies, power_spectrum

def plot_power_spectrum(signal, sr= 44100):
    '''plot the power spectrum of a signal'''
    frequencies, power_spectrum = compute_power_spectrum(signal, sr)
    plt.ion()
    plt.clf()
    plt.plot(frequencies, power_spectrum)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    plt.grid(alpha=0.3)
    plt.show()

def frequency_band_to_db(signal,freq_lower_bound = None,
    freq_upper_bound = None, baseline_power = None, sr = 44100):
    '''compute the intensity in a frequency band and convert to decibels
    signal              the audio signal
    freq_lower_bound    the lower bound of the frequency band
    freq_upper_bound    the upper bound of the frequency band
    baseline_power      the power of a comparison signal 
                        using the praat_baseline_power as default
    '''
    if baseline_power == None: baseline_power = praat_baseline_power
    frequencies, fft = compute_fft(signal, sr)
    if freq_lower_bound == None: lower_index = 0
    else:
        lower_index = np.where(frequencies >= freq_lower_bound)[0][0]
    if freq_upper_bound == None: upper_index= len(fft)
    else:
        upper_index = np.where(frequencies <= freq_upper_bound)[0][-1]
    intensity = 2*np.sum(np.abs(fft[lower_index:upper_index]/len(signal))**2)
    return 10 * np.log10(intensity/ baseline_power) 

def get_four_fb_to_db(signal, baseline_power = None, sr = 44100):
    '''compute the power in four frequency bands and convert to decibels
    the frequency bands are based on the article Sluijter & van Heuven (1994)
    to predict stress in vowels.
    '''
    fb1 = frequency_band_to_db(signal, 0, 500, baseline_power, sr = sr)
    fb2 = frequency_band_to_db(signal,500, 1000, baseline_power, sr = sr)
    fb3 = frequency_band_to_db(signal,1000, 2000, baseline_power, sr = sr)
    fb4 = frequency_band_to_db(signal,2000, 4000, baseline_power, sr = sr)
    return fb1, fb2, fb3, fb4


def make_dataset(language_name = 'dutch',
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    ''' create a dataset for the LDA training based on the vowel 
    spectral balance to predict stress in vowels.
    '''
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    spectral_tilts, stress = [], []
    for stress_status in vowel_stress_dict.keys():
        stress_value = 1 if stress_status == 'stress' else 0
        print(f'Processing {stress_status} {stress_value} vowels')
        for vowel in progressbar(vowel_stress_dict[stress_status]):
            spectral_tilt = vowel.spectral_tilt
            if not spectral_tilt or len(spectral_tilt) != 4: continue
            spectral_tilts.append(vowel.spectral_tilt)
            stress.append(stress_value)
    # return spectral_tilts, stress
    X, y = np.array(spectral_tilts), np.array(stress)
    return X, y

def train_lda(X, y, test_size = .33, report = True,random_state = 42):
    '''train an LDA based on the vowel spectral balance data
    X, y can be computed with the make_dataset function
    '''
    clf, data, report = lda.train_lda(X, y, test_size = test_size, 
        report = report, random_state = random_state)
    return clf, data, report

def plot_lda_hist(X, y, clf = None, new_figure = True, 
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = 'spectral tilt', xlim = None):
    '''plot distribution of LDA scores for stress and no stress vowels'''
    if not clf:
        clf, _, _ = train_lda(X, y, report = False)
    lda.plot_lda_hist(X, y, clf, new_figure = new_figure, 
        minimal_frame = minimal_frame, ylim = ylim, add_left = add_left,
        add_legend = add_legend, bins = bins, xlabel = xlabel, xlim = xlim)
    return clf
        






