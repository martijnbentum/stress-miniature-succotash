def select_words(word_list, language_name = 'dutch'):
    from text.models import Word
    words = Word.objects.filter(word__in = word_list, 
        language__language__iexact = language_name)
    return list(words)

def load_vowel_hidden_states(word_list, syllable_index = 0, mean = True,
    hs = 'cnn'):
    output = []
    words = []
    vowels = []
    for word in word_list:
        syllable = word.syllables[syllable_index]
        vowel = syllable.vowel
        if not vowel: continue
        vowel = vowel[0]
        if hs == 'cnn':
            hidden_states = vowel.cnn(mean = mean)
        else:
            hidden_states = vowel.transformer(layer = hs, mean = mean)
        output.append(hidden_states)
        words.append(word)
        vowels.append(vowel)
    return output, words, vowels

def word_to_lables(words):
    return [word.word for word in words]

def phoneme_to_labels(phonemes):
    return [phoneme.ipa for phoneme in phonemes]

def word_and_phoneme_to_labels(words, phonemes):
    output = []
    for word, phoneme in zip(words, phonemes):
        output.append(f'{phoneme.ipa} {word.word}')
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
    word_types = list(set([word.word for word in words]))
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

def plot_o_ij_words():
    words = select_o_ij_dutch_words()
    hidden_states, words, vowels = load_vowel_hidden_states(words)
    labels = word_and_phoneme_to_labels(words)
    tsne_hidden_states = tsne(hidden_states, perplexity = 10, n_iter = 1000, 
        apply_pca = True, pca_components = 50, scale_before_pca = True)
    plot_tsne(tsne_hidden_states, labels = labels)
    

