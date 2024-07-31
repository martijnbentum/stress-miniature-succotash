from collections import Counter
import itertools
import json
from load import load_bpc
import math
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from progressbar import progressbar
from scipy.stats import entropy

def phrases_to_text(phrases):
    '''Converts a list or queryset of phrases to a string of text.
    this is a grapheme representation of the phrases.
    '''
    text = []
    for phrase in phrases:
        text.append(phrase.phrase.lower())
    text = '\n'.join(text)
    return text

def phrases_to_ipa(phrases = None, language_name = 'dutch'):
    '''Converts a list or queryset of phrases to a string of IPA.
    this is a phonemic representation of the phrases.
    '''
    if not phrases:
        from text.models import Phrase, Language
        language = Language.objects.get(language__iexact = language_name)
        phrases = Phrase.objects.filter(language = language)
        print(f'loading all {language_name} phrases')
    text = []
    for phrase in phrases:
        text.append(phrase.ipa.replace('|', ' '))
    ipa ='\n'.join(text)
    return ipa

def make_ipa_char_set(ipa):
    '''Returns a list of unique characters in the IPA string.'''
    ipa = ipa.replace('\n', '  ')
    char_set = list(set(ipa.split(' ')))
    char_set[char_set.index('')] = ' '
    return char_set

def get_phonemes(language_name = 'dutch'):
    from text.models import Language, Phoneme
    language = Language.objects.get(language__iexact = language_name)
    phonemes = Phoneme.objects.filter(language = language)
    print(f'loading all {language_name} phonemes')
    return phonemes

def make_neighbour(ipa, index, n = 1, side = 'both'):
    if side == 'left':
        neighbour = '_'.join(ipa[index-n:index])
        return neighbour
    if side == 'right':
        neighbour = '_'.join(ipa[index+1:index+n+1])
        return neighbour
    if side != 'both':
        raise ValueError('side must be left, right or both')
    left = '_'.join(ipa[index-n:index])
    right = '_'.join(ipa[index+1:index+n+1])
    return '_'.join([left,right])

def collect_all_neighbours_from_neighbour_dict(neighbour_dict):
    neighbours = []
    for phoneme in neighbour_dict.keys():
        for neighbour in neighbour_dict[phoneme].keys():
            if neighbour not in neighbours:
                neighbours.append(neighbour)
    return neighbours

def phoneme_to_n_neighbour_dict(ipa = None, language_name = 'dutch', 
    n = 1, side = 'both'):
    '''Returns a dictionary of phonemes and their n neighbours.
    '''
    if not ipa: ipa = get_phonemes(language_name)
    neighbour_dict = {}
    for phrase in ipa.split('\n'):
        phrase = phrase.split(' ')
        for index, phoneme in enumerate(phrase):
            if phoneme == '': continue
            if index < n or index > len(phrase) - n - 1: continue
            if phoneme not in neighbour_dict.keys():
                neighbour_dict[phoneme] = {}
            neighbour = make_neighbour(phrase, index, n, side)
            if neighbour not in neighbour_dict[phoneme].keys():
                neighbour_dict[phoneme][neighbour] = 0
            neighbour_dict[phoneme][neighbour] += 1
    return neighbour_dict

def make_or_load_n_neighbour_dict(language_name, n = 1, side = 'both'):
    language_name = language_name.lower()
    filename = f'../data/{language_name}_{n}_{side}_neighbour_dict.json'
    if os.path.exists(filename): return load_json(filename)
    ipa = phrases_to_ipa(language_name = language_name)
    neighbour_dict = phoneme_to_n_neighbour_dict(ipa, n = n, side = side)
    save_dict_to_json(neighbour_dict, filename)
    return neighbour_dict

def make_neighbour_dicts(language_name = 'dutch', n = []):
    sides = 'left,right,both'.split(',')
    if not n: n = [1,2,3]
    for side in sides:
        for n_ in n:
            print(f'making {n_} {side} {language_name} neighbour dict')
            make_or_load_n_neighbour_dict(language_name, n = n_, side = side)
    

def phoneme_to_syllable_dict(phonemes = None, language_name = 'dutch'):
    if not phonemes: phonemes = get_phonemes(language_name)
    syllable_dict = {}
    for phoneme in progressbar(phonemes):
        if phoneme.ipa not in syllable_dict.keys():
            syllable_dict[phoneme.ipa] = {}
        syllable_ipa = phoneme.syllable.ipa
        if syllable_ipa not in syllable_dict[phoneme.ipa]:
            syllable_dict[phoneme.ipa][syllable_ipa] = 0
        syllable_dict[phoneme.ipa][syllable_ipa] += 1
    return syllable_dict

def phoneme_to_word_dict(phonemes = None, language_name = 'dutch'):
    if not phonemes: phonemes = get_phonemes(language_name)
    word_dict = {}
    for phoneme in progressbar(phonemes):
        if phoneme.ipa not in word_dict.keys():
            word_dict[phoneme.ipa] = {}
        word_ipa = phoneme.word.ipa
        if word_ipa not in word_dict[phoneme.ipa]:
            word_dict[phoneme.ipa][word_ipa] = 0
        word_dict[phoneme.ipa][word_ipa] += 1
    return word_dict

def load_or_make_phoneme_to_syllable_dict(language_name):
    language_name = language_name.lower()
    filename = f'../data/{language_name}_phoneme_syllable_dict.json'
    if os.path.exists(filename): return load_json(filename)
    phonemes = get_phonemes(language_name)
    sd = phoneme_to_syllable_dict(phonemes)
    save_dict_to_json(sd, filename)
    return sd

def load_or_make_phoneme_to_word_dict(language_name):
    language_name = language_name.lower()
    filename = f'../data/{language_name}_phoneme_word_dict.json'
    if os.path.exists(filename): return load_json(filename)
    phonemes = get_phonemes(language_name)
    wd = phoneme_to_word_dict(phonemes)
    save_dict_to_json(wd, filename)
    return wd

def load_or_make_all_phoneme_types(language_name):
    '''Returns a dictionary of phoneme types and their number of occurences.'''
    language_name = language_name.lower()
    filename = f'../data/{language_name}_phoneme_types.json'
    if os.path.exists(filename): return load_json(filename)
    from text.models import Language, Phoneme 
    language = Language.objects.get(language__iexact = language_name)
    phonemes = Phoneme.objects.filter(language = language)
    phoneme_types = {}
    for phoneme in progressbar(phonemes):
        phoneme_ipa = phoneme.ipa
        if phoneme_ipa not in phoneme_types.keys():
            phoneme_types[phoneme_ipa] = 0
        phoneme_types[phoneme_ipa] += 1
    phoneme_types = sort_dict(phoneme_types)
    save_dict_to_json(phoneme_types, filename)
    return phoneme_types

def load_or_make_all_syllable_types(language_name):
    '''Returns a dictionary of syllable types and their number of occurences.'''
    language_name = language_name.lower()
    filename = f'../data/{language_name}_syllable_types.json'
    if os.path.exists(filename): return load_json(filename)
    from text.models import Language, Syllable
    language = Language.objects.get(language__iexact = language_name)
    syllables = Syllable.objects.filter(language = language)
    syllable_types = {}
    for syllable in progressbar(syllables):
        syllable_ipa = syllable.ipa
        if syllable_ipa not in syllable_types.keys():
            syllable_types[syllable_ipa] = 0
        syllable_types[syllable_ipa] += 1
    syllable_types = sort_dict(syllable_types)
    save_dict_to_json(syllable_types, filename)
    return syllable_types

def load_or_make_all_word_types(language_name):
    '''Returns a dictionary of word types and their number of occurences.'''
    language_name = language_name.lower()
    filename = f'../data/{language_name}_word_types.json'
    if os.path.exists(filename): return load_json(filename)
    from text.models import Language, Word
    language = Language.objects.get(language__iexact = language_name)
    words = Word.objects.filter(language = language)
    word_types = {}
    for word in progressbar(words):
        word_ipa = word.ipa
        if word_ipa not in word_types.keys():
            word_types[word_ipa] = 0
        word_types[word_ipa] += 1
    word_types = sort_dict(word_types)
    save_dict_to_json(word_types, filename)
    return word_types
        

def load_full_syllable_dict(language_name, percentage = False):
    '''add all syllable types to the phoneme syllable dict.
    percentage returns the percentage of occurence for a syllable type 
    for each phoneme.
    '''
    sd = load_or_make_phoneme_to_syllable_dict(language_name)
    st = load_or_make_all_syllable_types(language_name)
    output = {}
    for phoneme in sd.keys():
        output[phoneme] = {}
        for syllable in st.keys():
            output[phoneme][syllable] = 0
            if syllable in sd[phoneme].keys():
                output[phoneme][syllable] = sd[phoneme][syllable]
    for phoneme in output.keys():
        for syllable in output[phoneme].keys():
            output[phoneme][syllable] += 1
    if percentage:
        for phoneme in output.keys():
            total = sum(output[phoneme].values())
            for syllable in output[phoneme].keys():
                output[phoneme][syllable] = output[phoneme][syllable]/total
    return output

def load_full_word_dict(language_name, percentage = False):
    '''add all word types to the phoneme word dict.
    percentage returns the percentage of occurence for a word type
    for each phoneme.
    '''
    wd = load_or_make_phoneme_to_word_dict(language_name)
    wt = load_or_make_all_word_types(language_name)
    output = {}
    for phoneme in wd.keys():
        output[phoneme] = {}
        for word in wt.keys():
            output[phoneme][word] = 0
            if word in wd[phoneme].keys():
                output[phoneme][word] = wd[phoneme][word]
    for phoneme in output.keys():
        for word in output[phoneme].keys():
            output[phoneme][word] += 1
    if percentage:
        for phoneme in output.keys():
            total = sum(output[phoneme].values())
            for word in output[phoneme].keys():
                output[phoneme][word] = output[phoneme][word]/total
    return output

def load_full_n_neighbour_dict(language_name, n = 1, side = 'both',
    percentage = False):
    '''add all neighbour types to the phoneme neighbour dict.
    '''
    d = make_or_load_n_neighbour_dict(language_name, n = n, side = side)
    neighbours = collect_all_neighbours_from_neighbour_dict(d)
    output = {}
    for phoneme in d.keys():
        output[phoneme] = {}
        for neighbour in neighbours:
            output[phoneme][neighbour] = 0
            if neighbour in d[phoneme].keys():
                output[phoneme][neighbour] = d[phoneme][neighbour]
    for phoneme in output.keys():
        for neighbour in output[phoneme].keys():
            output[phoneme][neighbour] += 1
    if percentage:
        for phoneme in output.keys():
            total = sum(output[phoneme].values())
            for neighbour in output[phoneme].keys():
                output[phoneme][neighbour] = output[phoneme][neighbour]/total
    return output

def save_dict_to_json(d, path):
    with open(path, 'w') as f:
        json.dump(d, f)

def load_json(path):
    with open(path, 'r') as f:
        d = json.load(f)
    return d
    

def ipa_char_occurence(ipa):
    ipa = ipa.replace('\n', ' ')
    return Counter(ipa.split(' '))


def plot_dict(d, y_label = 'entropy', x_label = 'Phoneme'):
    labels = list(d.keys())
    values = list(d.values())
    plt.figure()
    plt.bar(labels, values)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.grid(alpha=0.5)
    plt.show()

    
    
def compute_n_one_neighbour_contexts(ipa, to_percentage = False):
    d = ipa_to_one_neighbour(ipa)
    n = 0
    output = {}
    total = len(possible_one_neighbours(ipa))
    for char in d:
        n = len(d[char])
        if to_percentage: n = n/total
        output[char] = n
    return output
    
def sort_dict(d):
    '''sort a dict based on the values.'''
    sorted_dict = dict(sorted(d.items(), key=lambda item: item[1]))
    return sorted_dict

def make_kld_plots(language_name = 'dutch'):
    '''make kullback leibler divergence plots for a language.
    make plots for phoneme to syllable, phoneme to word, phoneme to neighbours.
    neighbours can be left, right, both and contain 1 - 3 neighbours.
    '''
    print('preparing',language_name)
    phoneme_types = load_or_make_all_phoneme_types(language_name)
    ipa_ordered = list(phoneme_types.keys())[::1]
    ipa_grouped, _, _ = load_bpc.group_phonemes(ipa_ordered)
    dicts, names, klds = [], [], []
    print('loading word and syllable dicts')
    dicts.append( load_full_word_dict(language_name, percentage = True) )
    names.append('word')
    dicts.append( load_full_syllable_dict(language_name, percentage = True) )
    names.append('syllable')
    print('loading neighbour dicts')
    for n in [1,2,3]:
        for side in 'left,right,both'.split(','):
            if n == 3 and side == 'both': continue
            print(f'loading {n} neighbour {side} dict')
            dicts.append(load_full_n_neighbour_dict(language_name, n = n, 
                side = side,percentage = True))
            names.append(f'{n}_neighbour_{side}')
    print('computing klds')
    for d, name in zip(dicts, names):
        kld = kullback_leibler_divergence(d, language_name, name)
        klds.append(kld)
        kld.plot(ipa_grouped, name = name)
        plt.savefig(f'../figures/{language_name}_{name}_kld_grouped.png')
        kld.plot(ipa_ordered, name = name)
        plt.savefig(f'../figures/{language_name}_{name}_kld_ordered.png')
    return dicts, names, klds
    


class kullback_leibler_divergence:
    '''Class for computing the kullback leibler divergence between 
    probability distributions of items for phoneme pairs.
    e.g. phoneme to syllable, phoneme to word, phoneme to neighbours.
    '''
    def __init__(self, percentage_dict = None, language_name = 'dutch',
        name = ''):
        if not percentage_dict:
            print(f'loading {language_name} full syllable dict')
            sd = load_full_syllable_dict(language_name, percentage = True)
            
        self.percentage_dict = percentage_dict
        self.language_name = language_name
        self.name = name
        self._compute_kl()

    def _check_pdf_order(self,key, other_key):
        pdf1_keys = self.percentage_dict[key].keys()
        pdf2_keys = self.percentage_dict[other_key].keys()
        for k1, k2 in zip(pdf1_keys, pdf2_keys):
            if k1 != k2:
                m = f'pdfs are not in the same order for {key} and {other_key}:'
                m += f'\t {k1} != {k2}'
                raise ValueError(m)

    def _compute_kl(self):
        '''Computes the kullback leibler divergence between the probability
        distributions of the items in the percentage_dict.
        e.g. kl phoneme n and phoneme m for probability distributions of
        syllables.
        '''
        self.kl_dict = {}
        keys = list(self.percentage_dict.keys())
        d = self.percentage_dict
        for key in keys:
            for other_key in keys:
                self._check_pdf_order(key, other_key)
                pdf1, pdf2 = list(d[key].values()), list(d[other_key].values())
                D = entropy(pdf1, pdf2, base = 2)
                self.kl_dict[key, other_key] = D

    def make_matrix(self, keys = None):
        '''Returns a matrix of the kullback leibler divergence between the
        probability distributions of the items in the percentage_dict.
        '''
        if not keys: keys = list(self.percentage_dict.keys())
        matrix = np.zeros((len(keys), len(keys)))
        for key in keys:
            for other_key in keys:
                index = keys.index(key), keys.index(other_key)
                matrix[index] = self.kl_dict[key, other_key]
        return matrix

    def plot(self, keys = None, name = ''):
        '''Plots the kullback leibler divergence matrix for 
        the percentage_dict.'''
        if not name: name = self.language_name + ' ' + self.name
        if not keys: keys = list(self.percentage_dict.keys())
        matrix = self.make_matrix(keys)
        plt.ion()
        fig, ax = plt.subplots(figsize=(8,6))
        img = ax.imshow(matrix, cmap='viridis', interpolation='nearest')
        x = np.arange(len(keys))
        ax.set_xticks(x)
        ax.set_yticks(x)
        ax.set_xticklabels(keys)
        ax.set_yticklabels(keys)
        fig.colorbar(img)
        plt.title(name)
        plt.show()
        return matrix



def plot_ipa_char_occurence(ipa = None, occurence = None, contexts = None, 
        entropy = None):
    '''Plots the occurence of phonemes in the IPA string, the percentage of
    different contexts for each phoneme and the entropy of the probability
    distribution of the neighbours of each phoneme.
    '''
    if not ipa: ipa = phrases_to_ipa()
    if not occurence: occurence = ipa_char_occurence(ipa)
    cl = occurence.most_common()
    if not contexts: 
        contexts = compute_n_one_neighbour_contexts(ipa, to_percentage = True)
    if not entropy:
        entropy = ipa_to_one_neighbour_entropy(ipa, normalised = True)
    labels = [c[0] for c in cl]
    values = [c[1] for c in cl]
    context_values = [contexts[c] for c in labels]
    entropy_values = [entropy[c] for c in labels]
    probs = [v/sum(values) for v in values]
    fig, ax1 = plt.subplots(sharey=True)
    width = 0.30
    x = np.arange(len(labels))
    b1 = ax1.bar(x-width, probs, width, label = 'Phoneme occurence', 
        color = 'orange')
    ax1.tick_params(axis='y', labelcolor='orange')
    ax2 = ax1.twinx()
    b2 = ax2.bar(x, context_values, width, label = 'Different contexts',
        color = 'black')
    ax2.tick_params(axis='y', labelcolor='black')
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    b3 = ax3.bar(x+width, entropy_values, width, label = 'normalized entropy',
        color = 'lightgrey')
    ax3.tick_params(axis='y', labelcolor='lightgrey')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    # plt.bar(labels, probs)
    ax1.set_yticks(np.linspace(0, 0.14, 8))
    ax2.set_yticks(np.linspace(0, 0.7, 8))
    ax3.set_yticks(np.linspace(0, 1, 8))
    ax1.grid(alpha=0.5)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper center')
    ax3.legend(loc='upper right')
    plt.show()
    return ipa, occurence, contexts, entropy
        

def ipa_to_one_neighbour_entropy(ipa = None, d= None, normalised = False):
    '''Computes the entropy of the probability distribution of the neighbours
    '''
    if not ipa and not d: ipa = phrases_to_ipa()
    if not d: d = ipa_to_one_neighbour(ipa, percentage = True)
    entropy_dict = {}
    for char in d:
        if normalised:
            n = len(d[char])
            H = entropy(list(d[char].values()), base = 2) 
            if normalised: H /= math.log2(n)
        entropy_dict[char] = H
    entropy_dict = sort_dict(entropy_dict)
    return entropy_dict

def ipa_to_one_neighbour(ipa, percentage = False, add_all_options = False):
    '''Returns a dictionary of phonemes with count dicts of their neighbours.
    '''
    d = {}
    if add_all_options:
        neighbours = possible_one_neighbours(ipa)
        for char in make_ipa_char_set(ipa):
            if char not in d: d[char] = {}
            for neighbour in neighbours:
                d[char][neighbour] = 1
    for line in ipa.split('\n'):
        line = line.split(' ')
        for i, char in enumerate(line):
            if char == '': continue
            if i == 0 or i == len(line) - 1: continue
            if char not in d: d[char] = {}
            neighbours = line[i-1], line[i + 1]
            if neighbours not in d[char]: d[char][neighbours] = 0
            d[char][neighbours] += 1
    for char in d:
        if not add_all_options:
            d[char] = sort_dict(d[char])
        if percentage:
            total = sum(d[char].values())
            for neighbour in d[char]:
                d[char][neighbour] = d[char][neighbour]/total
    return d

def one_neighbour_to_ipa(ipa, percentage = False):
    '''Returns a dictionary of neighbours with count dicts of the central 
    phoneme.
    '''
    d = {}
    for line in ipa.split('\n'):
        line = line.split(' ')
        for i, next_ in enumerate(line):
            if i < 2: continue
            char = line[i-1]
            neighbours = line[i-2], next_
            if neighbours not in d: d[neighbours] = {}
            if char not in d[neighbours]: d[neighbours][char] = 0
            d[neighbours][char] += 1
    for neighbours in d.keys():
        d[neighbours] = sort_dict(d[neighbours])
        if percentage:
            total = sum(d[neighbours].values())
            for char in d[neighbours]:
                d[neighbours][char] = d[neighbours][char]/total
    return d
            
def possible_one_neighbours(ipa):
    '''Returns a list of possible neighbours for each phoneme in the IPA string.
    '''
    char_set = make_ipa_char_set(ipa)
    o = list(itertools.product(char_set, repeat = 2))
    return o

def ipa_neighbour_kullback_leibler_divergence(ipa):
    '''Computes the kullback leibler divergence between the probability
    distributions of the neighbours of phonemes in the IPA string.
    '''
        
    d = ipa_to_one_neighbour(ipa, percentage = True, add_all_options = True)
    kl = {}
    for char in d.keys():
        for other_char in d.keys():
            pdf1, pdf2 = list(d[char].values()), list(d[other_char].values())
            D = entropy(pdf1, pdf2, base = 2)
            kl[char, other_char] = D
    return kl


def plot_kl_matrix(ipa):
    '''plots the kullback leibler divergence matrix for the IPA string.'''
    d = ipa_neighbour_kullback_leibler_divergence(ipa)
    occurence = ipa_char_occurence(ipa)
    cl = occurence.most_common()
    ipa_chars = [c[0] for c in cl]
    matrix = np.zeros((len(cl), len(cl)))
    for char in ipa_chars:
        for other_char in ipa_chars:
            index = ipa_chars.index(char), ipa_chars.index(other_char)
            matrix[index] = d[char, other_char]
    fig, ax = plt.subplots(figsize=(8,6))
    img = ax.imshow(matrix, cmap='viridis', interpolation='nearest')
    x = np.arange(len(ipa_chars))
    ax.set_xticks(x)
    ax.set_yticks(x)
    ax.set_xticklabels(ipa_chars)
    ax.set_yticklabels(ipa_chars)
    fig.colorbar(img)
    plt.show()
    return matrix
    
    
