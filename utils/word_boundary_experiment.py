# experiment to test whether bisyllabic words and combined syllables accross
# word boundaries have distinct representations.

from pathlib import Path
from utils import select
import numpy as np
from progressbar import progressbar

np.random.seed(42)

directory = Path('../word_boundary_test')

def make_or_load_all_ipas():
    filename = directory / 'all_bisyllabic_ipas.txt'
    if filename.exists():
        with filename.open('r') as f:
            return f.read().split('\n')
    words = select.select_words(language_name = 'dutch',  
        number_of_syllables = 2)
    ipas = []
    for word in progressbar(words):
        syllables = word.syllables
        if len(syllables) != 2: continue
        syl1, syl2 = syllables
        if not check_syllable_ok(syl1) or not check_syllable_ok(syl2):
            continue
        ipas.append( ','.join([syl1.ipa, syl2.ipa]) )
    with filename.open('w') as f:
        f.write('\n'.join(ipas))
    return ipas

def load_word_set():
    f = directory / 'bisyllabic_dutch_word_frequency-30-100.txt'
    with f.open('r') as file:
        selected_words = file.read().split('\n')
    from text.models import Word
    words = select.select_words(language_name = 'dutch',  
        number_of_syllables = 2)
    d = {}
    output = []
    for word in words:
        lemma = word.word.lower()
        if lemma not in selected_words: continue
        if lemma in d: d[lemma] += 1
        else: d[lemma] = 1
        if d[lemma] > 30: continue
        output.append(word)
    for k,v in d.items():
        if v < 30: print(k,v,'less than 30')
    return output

def word_set_to_audio_set(words = None):
    if words is None: words = load_word_set()
    audios = []
    for word in words:
        audio = word.audio
        if audio not in audios: audios.append(audio)
    return audios
       
def audios_to_phrase_set(audios = None):
    if audios is None: audios = word_set_to_audio_set()
    phrases = []
    for audio in audios:
        phrase = audio.phrase_set.all()
        if phrase.count() != 1: print('audio has more than one phrase',phrase)
        phrases.append(phrase[0])
    return phrases
    
class Phrase_info:
    def __init__(self, phrase, selected_words = None):
        self.phrase = phrase
        self.audio = phrase.audio
        self.words = phrase.words
        self.syllables = phrase.syllables
        self.syllable_count = len(self.syllables)
        self.word_count = len(self.words)
        self.sentence = ' '.join([word.word for word in self.words])
        self._set_selected_words_and_syllables(selected_words)

    def _set_selected_words_and_syllables(self, selected_words):
        if selected_words is None: selected_words = load_word_set()
        self.selected_words, self.selected_word_indices = [], []
        self.selected_syllables, self.selected_syllable_indices = [], []
        for word in self.words:
            if word in selected_words:
                self.selected_words.append(word)
                self.selected_word_indices.append(self.words.index(word))
                for syllable in word.syllables:
                    self.selected_syllables.append(syllable)
                    self.selected_syllable_indices.append(
                        self.syllables.index(syllable))
        self.selected_word_count = len(self.selected_words)
        self.selected_syllables_count = len(self.selected_syllables)

    def find_non_used_syllables(self):
        syllables = [syllable for syllable in self.syllables if 
            syllable not in self.selected_syllables]
        return syllables

    def select_syllable_pair_accross_word_boundary(self, used = False, 
        has_vowel = True, has_consonant = None, has_stress = None):
        syllable_pairs = list_to_pairs(self.syllables)
        syllable_pairs = remove_same_word_syllable_pairs(syllable_pairs)
        syllable_pairs = check_syllable_pairs_ok(syllable_pairs, has_vowel, 
            has_consonant, has_stress)
        if used:
            syllable_pairs = select_syllable_pair_with_used_syllable(
                syllable_pairs, self.selected_syllables)
        else:
            syllable_pairs = select_unused_syllable_pairs(syllable_pairs, 
                self.selected_syllables)
        if not syllable_pairs: return None
        return syllable_pairs

def check_syllable_ok(syllable, has_vowel = True, has_consonant = None,
    has_stress = None):
    if has_vowel:
        if not syllable.vowel: return False
        if len(syllable.vowel) != 1: return False
    if has_consonant:
        if not syllable.onset and not syllable.coda: return False
    if has_stress and not syllable.stress: return False
    return True
    
def check_syllables_in_same_word(syllable1, syllable2):
    return syllable1.word == syllable2.word
    
def list_to_pairs(l):
    return [(l[i],l[i+1]) for i in range(len(l)-1)]

def remove_same_word_syllable_pairs(syllable_pairs):
    return [pair for pair in syllable_pairs if not
        check_syllables_in_same_word(pair[0],pair[1])]

def check_syllable_pair_ok(syllable1, syllable2, has_vowel = True, 
    has_consonant = None, has_stress = None):
    if not check_syllable_ok(syllable1, has_vowel, has_consonant, has_stress):
        return False
    if not check_syllable_ok(syllable2, has_vowel, has_consonant, has_stress):
        return False
    return True

def check_syllable_pairs_ok(syllable_pairs, has_vowel = True, 
    has_consonant = None, has_stress = None):
    output = []
    for syllable_pair in syllable_pairs:
        syllable1, syllable2 = syllable_pair
        if check_syllable_pair_ok(syllable1, syllable2, has_vowel, 
            has_consonant, has_stress):
            output.append(syllable_pair)
    return output

def check_syllable_in_syllable_list(syllable, syllable_list):
    return syllable in syllable_list

def check_syllable_pair_in_syllable_list(syllable1, syllable2, syllable_list):
    return check_syllable_in_syllable_list(syllable1,syllable_list) or \
        check_syllable_in_syllable_list(syllable2,syllable_list)


def select_unused_syllable_pairs(syllable_pairs, used_syllables):
    output = []
    for syllable_pair in syllable_pairs:
        syllable1, syllable2 = syllable_pair
        if not check_syllable_pair_in_syllable_list(syllable1, syllable2, 
            used_syllables):
            output.append(syllable_pair)
    return output

def select_syllable_pair_with_used_syllable(syllable_pairs, used_syllables):
    output = []
    for syllable_pair in syllable_pairs:
        syllable1, syllable2 = syllable_pair
        if check_syllable_pair_in_syllable_list(syllable1, syllable2, 
            used_syllables):
            output.append(syllable_pair)
    return output

def save_syllable_pair(syllables, filename, audio_id = None, all_ipas = None):
    if not all_ipas: all_ipas = make_or_load_all_ipas()
    ids = ','.join([syllable.identifier for syllable in syllables])
    ipas = ','.join([syllable.ipa for syllable in syllables])
    stress = ','.join([str(int(syllable.stress)) for syllable in syllables])
    words = ','.join([syllable.word.word for syllable in syllables])
    starts = ','.join([str(syllable.start_time) for syllable in syllables])
    ends = ','.join([str(syllable.end_time) for syllable in syllables])
    start = str(syllables[0].start_time)
    end = str(syllables[-1].end_time)
    is_a_word = str(int(ipas in all_ipas))
    if not audio_id: audio_id = syllables[0].audio.identifier
    with open(filename,'a') as f:
        f.write('\t'.join([ipas, ids, stress, words, starts, ends, 
            is_a_word, start, end, audio_id])  + '\n')

def make_filename(used, has_vowel, has_consonant, has_stress):
    filename = f'syllable-pairs_used-{used}_vowel-{has_vowel}_'
    filename += f'consonant-{has_consonant}_stress-{has_stress}.txt'
    return directory / filename

def make_syllable_pairs_dataset(phrases = None, words = None,
    used = False, has_vowel = True, has_consonant = None, has_stress = None,
    all_ipas = None):
    if not words: words = load_word_set()
    if not phrases:
        audios = word_set_to_audio_set(words)
        phrases = audios_to_phrase_set(audios)
    if not all_ipas:
        all_ipas = make_or_load_all_ipas()
    filename = make_filename(used, has_vowel, has_consonant, has_stress)
    no_pairs = []
    phrase_infos = []
    for phrase in progressbar(phrases):
        pi = Phrase_info(phrase, words)
        phrase_infos.append(pi)
        syllable_pairs = pi.select_syllable_pair_accross_word_boundary(
            used = False, has_vowel = True, has_consonant = None,
            has_stress = None)
        if not syllable_pairs: 
            no_pairs.append(phrase)
            continue
        identifier = phrase.audio.identifier
        for pair in syllable_pairs:
            save_syllable_pair(pair, filename, identifier, all_ipas = all_ipas) 
    return phrase_infos, no_pairs


def load_syllable_pair_dataset(used = False, has_vowel = True, 
    has_consonant = None, has_stress = None):
    filename = make_filename(used, has_vowel, has_consonant, has_stress)
    with open(filename,'r') as f:
        lines = f.read().split('\n')
    output = []
    for line in lines:
        if not line: continue
        l = line.split('\t')
        ipas, ids, stress,words,starts,ends, is_a_word, start, end, audio_id=l
        d = {'ipas':ipas, 'ids':ids, 'stress':stress, 'words':words, 
            'starts':starts, 'ends':ends, 'is_a_word':int(is_a_word), 
            'start':float(start), 'end':float(end),
            'audio_id':audio_id}
        d['ids'] = d['ids'].split(',')
        d['stress'] = map(int,d['stress'].split(','))
        d['words'] = d['words'].split(',')
        d['starts'] = map(float,d['starts'].split(','))
        d['ends'] = map(float,d['ends'].split(','))
        output.append(d)
    return output

    

