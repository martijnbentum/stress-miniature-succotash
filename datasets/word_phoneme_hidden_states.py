from utils import load_hidden_states as lhs
import numpy as np
from utils import tsne

def select_words(word_list, language_name = 'dutch'):
    from text.models import Word
    words = Word.objects.filter(word__in = word_list, 
        language__language__iexact = language_name)
    return list(words)

def load_segment_hidden_states(word_list, syllable_index = 0, mean = True,
    hs = 'cnn', segment_type = 'vowel'):
    assert segment_type in ['onset', 'vowel', 'rime', 'coda', 'syllable','word']
    output, words, segments = [], [], []
    for word in word_list:
        if segment_type == 'word': segment = word.phonemes
        else:
            syllable = word.syllables[syllable_index]
            if segment_type == 'syllable': segment = syllable.phonemes
            else: segment= getattr(syllable, segment_type)
        if not segment: continue
        hidden_states = lhs.phoneme_list_to_combined_hidden_states(
            segment, hs = hs, mean = mean)
        output.append(hidden_states)
        words.append(word)
        segments.append(segment)
    return output, words, segments

def word_to_lables(words):
    return [word.word for word in words]

def phoneme_to_labels(phonemes):
    return [phoneme.ipa for phoneme in phonemes]

def word_and_phoneme_to_labels(words, phonemes, use_word_orthography = False):
    output = []
    for word, segments in zip(words, phonemes):
        ipa = '-'.join([x.ipa for x in segments])
        if use_word_orthography:
            output.append(f'{ipa} {word.word.lower()}')
        else:
            word_ipa = word.ipa.replace(' ','')
            output.append(f'{ipa} {word_ipa}')
    return output

def labels_to_numbers(labels):
    label_set = sorted(list(set(labels)))
    label_dict = {label: i for i, label in enumerate(label_set)}
    return [label_dict[label] for label in labels], reverse_dict(label_dict)

def reverse_dict(dictionary):
    '''reverse dictionary
    '''
    return {v: k for k, v in dictionary.items()}

def sample_words_by_type(words, max_tokens = 100):
    word_types = list(set([word.word.lower() for word in words]))
    count_dict = {}
    output = []
    for word in words:
        lemma = word.word
        if lemma not in count_dict:
            count_dict[lemma] = 0
        count_dict[lemma] += 1
        if count_dict[lemma] > max_tokens:
            continue
        output.append(word)
    return output
        
def make_phoneme_word_marker_dict(label_dict):
    output = {}
    markers = 'o', 's', '^', 'D', '<', '>', 'v', 'P', 'X', 'H'
    markers += '+', 'x', '1', '2', '3', '4', '8', 'p', 'h', 'd'
    markers += '|', '_', '.', ',', 'h'
    items = list(set([v.split(' ')[0] for v in label_dict.values()]))
    for k, v in label_dict.items():
        item = v.split(' ')[0]
        output[k] = markers[items.index(item)]
    return output

def select_o_ij_dutch_words():
    ij_words = ['zijn','bijl','wijn','pijp','rijk']
    o_words = ['zon','bol','won','pop','rok']
    words = ij_words + o_words
    output = select_words(words)
    output = sample_words_by_type(output)
    return output

def plot_words(words = None, segment_types = ['vowel'], hs_types = [],
    save = False, name = 'o_ij_dutch_words.pdf', use_word_orthography = False):
    from matplotlib import pyplot as plt
    if not words: words = select_o_ij_dutch_words()
    if not hs_types: hs_types = ['cnn', 11, 21]
    n_columns = len(hs_types)
    n_rows = len(segment_types)
    plt.ion()
    fig, axes = plt.subplots(n_rows, n_columns, figsize = [18.6 ,  6*n_rows])
    for column_index, hs in enumerate(hs_types):
        for row_index, segment_type in enumerate(segment_types):
            if len(segment_types) == 1 or len(hs_types) == 1:
                ax = axes[column_index]
            else: 
                ax = axes[row_index, column_index]
            title = f'{segment_type} {hs}'
            hidden_states, w, segments= load_segment_hidden_states(words,
                hs = hs, segment_type = segment_type)
            labels=word_and_phoneme_to_labels(w,segments,use_word_orthography) 
            numbers, label_dict = labels_to_numbers(labels)
            marker_dict = make_phoneme_word_marker_dict(label_dict)
            X = tsne.tsne(np.array(hidden_states))
            add_legend = True if column_index == len(hs_types) -1 else False
            tsne.plot_tsne(X, numbers, label_dict, marker_dict, title, ax = ax,
                add_legend = add_legend, legend_outside = True)
    plt.show()
    plt.tight_layout()
    if save:
        hs = '-'.join([str(x) for x in hs_types])
        segment = '-'.join(segment_types)
        filename = f'../figures/{segment}_{hs}_{name}'
        plt.savefig(filename)
    return fig
    # plt.tight_layout(rect=[0, 0, 0.99, 1])

    

