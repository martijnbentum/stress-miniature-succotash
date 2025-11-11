from audio.audio import load_audio
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path
from scipy.signal import hilbert, butter, filtfilt, find_peaks
from text.models import Word, Syllable, Language, Dataset, Audio
from w2v2_hidden_states import frame

def get_audios(language_name = 'Dutch', dataset_name = 'COMMON VOICE'):
    l = Language.objects.get(language__iexact = language_name)
    d = Dataset.objects.get(name__iexact = dataset_name)
    audios = Audio.objects.filter(language = l, dataset = d)

def get_all_word_boundaries(audios = None, language_name = 'Dutch', 
    dataset_name = 'COMMON VOICE'):
    if audios is None: audios = get_audios(language_name, dataset_name)
    all_boundaries = {}
    for audio in audios:
        boundaries = get_word_boundaries(audio)
        all_boundaries[audio.filename] = boundaries
    return all_boundaries

def get_all_syllable_boundaries(audios = None, language_name = 'Dutch', 
    dataset_name = 'COMMON VOICE'):
    if audios is None: audios = get_audios(language_name, dataset_name)
    l = Language.objects.get(language__iexact = language_name)
    d = Dataset.objects.get(name__iexact = dataset_name)
    audios = Audio.objects.filter(language = l, dataset = d)
    all_boundaries = {}
    for audio in audios:
        boundaries = get_syllable_boundaries(audio)
        all_boundaries[audio.filename] = boundaries
    return all_boundaries

def get_word_boundaries(audio):
    '''load all words for an audio file and return their boundaries
    '''
    words = audio.word_set.all()
    f = Path(audio.filename).name
    boundaries = [(x.start_time,x.end_time, x.word, f) for x in words]
    return boundaries

def get_syllable_boundaries(audio):
    '''load all syllables for an audio file and return their boundaries
    '''
    syllables = audio.syllable_set.all()
    f = Path(audio.filename).name
    boundaries = [(x.start_time,x.end_time, x.ipa, f) for x in syllables]
    return boundaries

def syllable_durations(audios = None):


def plot_audio(audio, width = 12, cutoff_frequency = 5.0):
    word_boundaries = get_word_boundaries(audio)
    syllable_boundaries = get_syllable_boundaries(audio)
    syllable_mids = mid_points(syllable_boundaries)
    signal, sr = load_audio(audio)
    envelope = hilbert_envelope(signal, sample_rate = sr)
    envelope_peaks = peak_times_from_envelope(envelope, sample_rate = sr)
    x = np.arange(len(signal)) / sr
    min_y = np.min(signal)
    max_y = np.max(signal)
    text_y = min_y - (abs(min_y) * .2)
    min_x = word_boundaries[0][0] - 0.1
    max_x = word_boundaries[-1][1] + 0.1
    plt.ylim(text_y, max_y)
    plt.figure(figsize=(width, 4))
    plt.plot(x, signal, alpha=0.7, color = 'gray')
    plt.plot(x, envelope, color='black', linewidth=1.5, label='envelope')
    plt.vlines([wb[0] for wb in word_boundaries], ymin=0, ymax=max_y,
        colors='red', linestyles=(0,(5,5)), label='start word')
    plt.vlines([wb[1] for wb in word_boundaries], ymin=0, ymax=max_y,
        colors='orange', linestyles=(0,(3,3)), label='end word')
    plt.vlines([sb[0] for sb in syllable_boundaries], ymin=text_y, ymax=0, 
        colors='blue', linestyles=(0, (5,5)), label='start syllable')
    plt.vlines([sb[1] for sb in syllable_boundaries], ymin=text_y, ymax=0,
        colors='cyan', linestyles=(0,(3,3)),label='end syllable')
    plt.vlines([sb for sb in syllable_mids], ymin=0, ymax=max_y,
        colors='#1DACD6', linestyles=':',label='mid syllable')
    plt.vlines([p for p in envelope_peaks], ymin=0, ymax=max_y,
        colors='black', linestyles=(1,(1,1,1)),label='envelope peak', alpha = .6)
    for wb in word_boundaries:
        plt.text((wb[0]+wb[1])/2, 0, wb[2], color='red', 
            horizontalalignment='center', verticalalignment='top',
            fontsize=12, rotation=90)
    for sb in syllable_boundaries:
        plt.text((sb[0]+sb[1])/2, text_y, sb[2], color='blue', 
            horizontalalignment='center', verticalalignment='bottom',
            fontsize=12, rotation=90)
    plt.legend(loc='upper right')
    plt.grid(alpha=0.3)
    plt.xlim(min_x, max_x)
    plt.show()
        

def hilbert_envelope(signal, smooth_envelope = True, cutoff_frequency = 5.0,
    sample_rate = 16_000):
    '''compute the hilbert envelope of a signal'''
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)
    if smooth_envelope:
        amplitude_envelope = smooth(amplitude_envelope, cutoff_frequency)
    return amplitude_envelope

def smooth(signal, cutoff_frequency = 5.0, order = 4, sample_rate = 16_000,
    convolve = True):
    nyquist = 0.5 * sample_rate
    normal_cut_off = cutoff_frequency / nyquist
    b, a = butter(order, normal_cut_off, btype='low', analog=False)
    smoothed_signal = filtfilt(b, a, signal)
    if convolve:
        window_size = 1200
        window = np.ones(window_size) / window_size
        smoothed_signal= np.convolve(smoothed_signal, window, mode='same')
    return smoothed_signal

def mid_point(start, end):
    return (start + end) / 2

def mid_points(boundaries):
    return [mid_point(b[0], b[1]) for b in boundaries]

def peak_times_from_envelope(env, sample_rate=16_000, 
    min_interval_ms=80, prominence=None):
    distance = int(sample_rate * (min_interval_ms/1000))
    peaks, _ = find_peaks(env, distance=distance, prominence=prominence)
    return peaks / sample_rate
