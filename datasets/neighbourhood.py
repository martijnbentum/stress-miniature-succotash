from collections import Counter
from datasets import word_phoneme_hidden_states as wphs
from text.models import Word
import Levenshtein
from progressbar import progressbar
import random

def count_difference_for_position(word1, word2, difference_position):
    assert difference_position is not None
    difference_count = 0
    for syllable1, syllable2 in zip(word1, word2):
        segment1 = getattr(syllable1, difference_position)
        segment2 = getattr(syllable2, difference_position)
        if segment1 != segment2:
            difference_count += 1
    return difference_count


def count_difference(word1, word2):  
    ipa1 = word1.ipa.split(' ')
    ipa2 = word2.ipa.split(' ')
    return Levenshtein.distance(ipa1, ipa2)


def find_neighbours(word, difference = 1, difference_position = None):
    assert difference_position in [None, 'onset', 'vowel', 'coda']
    w = Word.objects.filter(language = word.language, dataset = word.dataset)
    homophone, same_word, neighbour = [], [], []
    for x in progressbar(w):
        if word.word.lower() == x.word.lower():
            same_word.append(x)
            continue
        if not difference_position:
            d = count_difference(word, x)
        else:
            d = count_difference_for_position(word, x, difference_position)
        if d == 0:
            homophone.append(x)
        if d <= difference:
            neighbour.append(x)
    neighbour_word_types = Counter([x.word.lower() for x in neighbour])
    return neighbour, same_word, homophone, neighbour_word_types

def make_ipa_to_word_dict(words, ipa_dict = {}):
    for word in words:
        if word.ipa not in ipa_dict.keys():
            ipa_dict[word.ipa] = []
        ipa_dict[word.ipa].append( word )
    return ipa_dict

def ipa_dict_to_dataset(ipa_dict, min_n = 10, max_n = 100):
    dataset = []
    for ipa, words in ipa_dict.items():
        if len(words) < min_n:
            continue
        if len(words) > max_n:
            words = random.sample(words,max_n)
        dataset.extend(words)
    return dataset

def make_dataset(word, difference = 1, difference_position = None, 
        min_n = 10, max_n = 100):
    neighbour, same_word, homophone, neighbour_word_types = find_neighbours(
        word, difference, difference_position)
    ipa_dict = make_ipa_to_word_dict(neighbour)
    ipa_dict = make_ipa_to_word_dict(same_word, ipa_dict)
    dataset = ipa_dict_to_dataset(ipa_dict, min_n, max_n)
    return dataset

def plot_dataset(source_word, dataset = None, segment_types = ['word'], 
    hs_types = [], save = False, name = 'neighbourhood.pdf', 
    use_word_orthography = True):
    if not dataset: dataset = make_dataset(source_word)
    if save:
        word = source_word.word.lower()
        name = word + '_' + name 
    wphs.plot_words(dataset, segment_types, hs_types, save, name, 
        use_word_orthography = use_word_orthography)

