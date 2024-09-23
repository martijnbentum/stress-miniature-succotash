# experiment to test whether bisyllabic words and combined syllables accross
# word boundaries have distinct representations.

from pathlib import Path
from utils import select
import numpy as np

np.random.seed(42)

directory = Path('../word_boundary_test')

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

    def find_non_used_syllables(self, has_vowel, has_consonant, has_stress):
        syllables = [syllable for syllable in self.syllables if 
            syllable not in self.selected_syllables[1:]]
        syllables = [syllable for syllable in syllables if 
            check_syllable_ok(syllable,has_vowel,has_consonant,has_stress)]
        return syllables

    def _find_used_start_syllable(self, has_vowel, has_consonant, has_stress):
        selected_syllables = self.selected_syllables[:]
        selected_syllables = np.random.shuffle(selected_syllables)
        for syllable in self.selected_syllables:
            if check_syllable_ok(syllable,has_vowel,has_consonant,has_stress):
                return syllable
        raise ValueError('no used start syllable found', 'has_vowel:',has_vowel,
            'has_consonant:',has_consonant,'has_stress:',has_stress)

    def _find_start_syllable(self, used, has_vowel, has_consonant, has_stress):
        if used: return self._find_used_start_syllable(has_vowel,has_consonant,
            has_stress)
        syllables = self.find_non_used_syllables(has_vowel, has_consonant,
            has_stress)
        syllable = np.random.choice(syllables, 1, False)[0]
        self.selected_syllables.append(syllable)
        self.selected_syllable_indices.append(
            self.syllables.index(syllable))
        return syllable

    def _find_other_syllable(self, start_syllable, has_vowel, has_consonant, 
        has_stress):
        syllables = self.find_non_used_syllables(has_vowel, has_consonant,
            has_stress)
        index = self.syllables.index(start_syllable)
        if index > 0: before = self.syllables[index-1]
        else: before = None
        if index < len(self.syllables)-1: after = self.syllables[index+1]
        else: after = None
        if before in syllables and after in syllables:
            return np.random.choice([before,after],1,False)[0]
        if before in syllables: return before
        if after in syllables: return after
        return None

    def select_syllables_accross_word_boundary(self, used = False, 
        has_vowel = True, has_consonant = None, has_stress = None):
        start_syllable = self._find_start_syllable(used, has_vowel,
            has_consonant, has_stress)
        if not start_syllable:
            raise ValueError('could not find start syllable')
        other_syllable = self._find_other_syllable(start_syllable, has_vowel, 
            has_consonant, has_stress)
        if not other_syllable:
            raise ValueError('could not find second syllable', start_syllable)
        return start_syllable, other_syllable
            
        

        

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

