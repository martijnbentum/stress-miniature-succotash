from collections import Counter
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from progressbar import progressbar
from scipy.stats import gaussian_kde
from .general import flatten_list
from . import model_names
from . import general

def load_audios():
    from text.models import Audio
    a = Audio.objects.filter(duration__lt = 300)
    audios = list(a[:100])
    return audios

def load_words(audios = None):
    if audios is None: audios = load_audios()
    words = []
    for audio in progressbar(audios):
        words.extend(list(audio.word_set.all()))
    return words

def load_phonemes(words = None, audios = None,):
    if words is None: words = load_words(audios)
    phonemes = []
    for word in progressbar(words):
        phonemes.extend(word.phonemes)
    return phonemes

def load_audio_words_phonemes(audios = None, words = None):
    if audios is None: 
        print('Loading audios')
        audios = load_audios()
    if words is None: 
        print('Loading words')
        words = load_words(audios)
    print('Loading phonemes')
    phonemes = load_phonemes(words = words)
    return audios, words, phonemes

def ipa_to_phoneme_dict(phonemes = None):
    if phonemes is None: phonemes = load_phonemes()
    ipas = [x.ipa for x in phonemes]
    ipa = Counter(ipas)
    phoneme_dict = {}
    for k, _ in progressbar(ipa.most_common()):
        phoneme_dict[k] = []
        for i, x in enumerate(ipas):
            if x == k:
                phoneme_dict[k].append(phonemes[i])
    return phoneme_dict

def speaker_to_phoneme_dict(phonemes):
    speaker_dict = {}
    for p in progressbar(phonemes):
        if p.speaker not in speaker_dict:
            speaker_dict[p.speaker] = []
        speaker_dict[p.speaker].append(p)
    return speaker_dict
    

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

def phonemes_to_codevector_indices(phoneme_list, model_name):
    o = []
    not_found = []
    for phoneme in progressbar(phoneme_list):
        ci = phoneme.codebook_indices(model_name)
        if len(ci) == 0:
            not_found.append(phoneme)
            continue
        ci = [list(map(int,x)) for x in ci]
        o.append(ci)
    flat_o = flatten_list(o)
    return o, flat_o, not_found

def phonemes_to_codevector_indices_model_set(phoneme_list, model_set):
    d = {}
    for model_name in model_set:
        o, flat_o, not_found = phonemes_to_codevector_indices(phoneme_list, 
            model_name)
        d[model_name] = {
            'codevector_indices': o,
            'not_found': not_found
        }
    return d

def collect_codevector_indices(phonemes = None, language = 'nl', 
    phoneme_set = None, limit = 1000, filename = None, overwrite = False,):

    if filename is None:
        filename = f'../{language}_phoneme_codevector_indices_{limit}.json'
    if Path(filename).exists() and not overwrite:
        print('loaded phoneme codevector indices from', filename)
        print('this is only based on filename not on other parameters')
        with open(filename, 'r') as f:
            d = json.load(f)
        return d

    if phonemes is None: phonemes = load_phonemes()
    model_set = model_names.select_model_set_by_language(language)
    itp = ipa_to_phoneme_dict(phonemes)
    if phoneme_set is None: phoneme_set = list(itp.keys())
    d = {}
    for phoneme in progressbar(phoneme_set):
        phoneme_list = itp[phoneme]
        if len(phoneme_list) > limit:
            phoneme_list = phoneme_list[:limit]
        d[phoneme] = {}
        for model_name in progressbar(model_set):
            print('handling model', model_name, 'phoneme', phoneme)
            o, flat_o, not_found = phonemes_to_codevector_indices(phoneme_list, 
                model_name)
            if phoneme not in itp:
                itp[phoneme] = {}
            d[phoneme][model_name] = {
                'o': o,
                'flat_o': flat_o,
                'not_found': not_found
            }
    with open(filename, 'w') as f:
        json.dump(d, f)
    return d

def combine_codevector_indices_per_model(d = None):
    if d is None:
        d = collect_codevector_indices()
    output = {}
    for phoneme, model_dict in d.items():
        for model_name, outputs in model_dict.items():
            if model_name not in output:
                output[model_name] = []
            output[model_name].extend(outputs['flat_o'])
    return output
        

def plot_codevector_indices_distribution_per_model(d = None, name = ''):
    if d is None:
        d = collect_codevector_indices()
    output = combine_codevector_indices_per_model(d)
    x, entropies, nmaxs, nmins, ns = [], [], [], [], []
    for model_name, indices in output.items():
        c = Counter(indices)
        nmax = max(c.values())
        nmin = min(c.values())
        n = len(c)
        entropy = general.compute_entropy(c)
        cp = int(model_name.split('-')[1])
        x.append(cp)
        entropies.append(entropy)
        nmaxs.append(nmax)
        nmins.append(nmin)
        ns.append(n)
    entropies, entropies_min, entropies_max = min_max_normalize(entropies)
    nmaxs, nmaxs_min, nmaxs_max = min_max_normalize(nmaxs)
    nmins, nmins_min, nmins_max = min_max_normalize(nmins)
    ns, ns_min, ns_max = min_max_normalize(ns)
    plt.figure(figsize=(9,4))
    label = _make_label('Entropy', entropies_min, entropies_max)
    plt.plot(x, entropies, label = label, color = 'red')
    label = _make_label('Max Count', nmaxs_min, nmaxs_max)    
    plt.plot(x, nmaxs, label = label, color = 'blue')
    label = _make_label('Min Count', nmins_min, nmins_max)
    plt.plot(x, nmins, label = label, color = 'green')
    label = _make_label('Unique Count', ns_min, ns_max)
    plt.plot(x, ns, label = label, color = 'orange')
    plt.title(f'Codevector indices distribution per model checkpoint ({name}) ')
    plt.xlabel('Model n training steps')
    plt.legend(prop={'family': 'monospace'})
    plt.grid(alpha = 0.5)
    plt.show()

def _make_label(name, min_value, max_value):
    label = name.ljust(12) + f' min: {min_value}'.ljust(10) 
    label += f' max: {max_value}'
    return label
    
def min_max_normalize(data):
    min_value = min(data)
    max_value = max(data)
    data = [(x - min_value) / (max_value - min_value) for x in data]
    if type(min_value) == float: 
        min_value = round(min_value, 2)
        max_value = round(max_value, 2)
    return data, min_value, max_value

    


    

def plot_counter(counter, title = 'Counter Plot', xlabel = 'Key', 
    ylabel = 'Count', sort_on= 'keys', limit = 100):
    if sort_on == 'keys':
        keys = sorted(counter.keys())
        values = [str(counter[k]) for k in keys]
    elif sort_on == 'values':
        temp = counter.most_common()
        keys = [str(x[0]) for x in temp]
        values = [x[1] for x in temp]
    keys, values = keys[:limit], values[:limit]
    plt.figure(figsize=(12,3))
    plt.plot(keys, values)
    if type(keys[0]) == str:
        plt.xticks(list(range(len(keys))), labels = keys, rotation = 90)
    else:
        plt.xticks(keys, labels = keys, rotation = 90)
    plt.title('Counter Plot')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha = 0.5)
    plt.show()
     

        
