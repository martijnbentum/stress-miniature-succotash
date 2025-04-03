from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

def load_audios():
    from text.models import Audio
    a = Audio.objects.filter(duration__lt = 300)
    audios = list(a[:100])
    return audios

def load_words(audios = None):
    if audios is None: audios = load_audios()
    words = []
    for audio in audios:
        words.extend(list(audio.word_set.all()))
    return words

def load_phonemes(audios = None, words = None):
    if words is None: words = load_words(audios)
    phonemes = []
    for word in words:
        phonemes.extend(word.phonemes)
    return phonemes

def density_plot(data, min_value = None, max_value = None, n_samples = 1000,
    title = 'Density Plot', xlabel = 'Value', ylabel = 'Density'):
    if min_value is None:
        min_value = min(data)
    if max_value is None:
        max_value = max(data)
    x = np.linspace(min_value, max_value, n_samples)
    y = gaussian_kde(data, bw_method = 'scott')(x)
    plt.figure(figsize = (6, 3))
    plt.plot(x, y, linewidth = 2, color = 'red', alpha = 0.5)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha = 0.5)
    plt.show()

def plot_phoneme_durations(phonemes = None, max_value = .2):
    if phonemes is None: phonemes = load_phonemes()
    durations = [p.duration for p in phonemes]
    density_plot(durations, title = 'Phoneme Durations', xlabel ='Duration (s)',
        max_value = max_value, ylabel = 'Density')
    plt.tight_layout()
    plt.show()
    return phonemes

def plot_word_durations(words = None, max_value = 1):
    if words is None: words = load_words()
    durations = [w.duration for w in words]
    density_plot(durations, title = 'Word Durations', xlabel ='Duration (s)',
        max_value = max_value, ylabel = 'Density')
    plt.tight_layout()
    plt.show()
    return words

def plot_phoneme_counts(phonemes = None):
    if phonemes is None: phonemes = load_phonemes()
    ipa = Counter([x.ipa for x in phonemes])
    plt.figure(figsize=(12,3))
    plt.bar(range(len(ipa)), [x[1] for x in ipa.most_common()])
    plt.xticks(range(len(ipa)), [x[0] for x in ipa.most_common()])
    plt.tight_layout()
    plt.show()
    return phonemes

def plot_word_counts(words = None, top_n_words = 70):
    if words is None: words = load_words()
    n = top_n_words
    c = Counter([x.word for x in words])
    plt.figure(figsize=(12,3))
    plt.bar(range(n), [x[1] for x in c.most_common()[:n]])
    plt.xticks(range(n), [x[0] for x in c.most_common()[:n]], rotation = 90)
    plt.title(f'Word Counts for top {n} words')
    plt.grid(alpha = 0.5)
    plt.tight_layout()
    plt.show()
    return words
