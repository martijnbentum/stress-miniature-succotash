from utils import align_phonemes
from utils import needleman_wunch as nw
from utils import celex
import json

class Aligner:
    def __init__(self,word, celex_database = None):
        self.word = word
        self.word_phonemes = self.word.phoneme_set.all()
        self._handle_celex(celex_database)
        self._get_stressed_syllable_based_on_index()
        self._align()
        self._get_stressed_syllable_based_on_stressed_vowel()
        self._set_info()
        self._compute_similarity_score()
        self.match = (self.stressed_syllable_based_on_index == 
            self.stressed_syllable_based_on_vowel)
        self.select_best_match()
    
    def __repr__(self):
        return self.word.__repr__()

    def __str__(self):
        n = 20
        m = 'Word (ort):'.ljust(n) + f'{self.word.word}\n'
        m += 'Word:'.ljust(n) + f'{self.word.ipa}\n'
        cw = self.celex_word.ipa if self.celex_word else 'None'
        m += 'Celex word:'.ljust(n) + f'{cw}\n'
        if self.celex_word:
            m += 'word nw:'.ljust(n) + f'{self.word_ipa_simple}\n'
            m += 'Celex nw:'.ljust(n) + f'{self.celex_ipa_simple}\n'
        syllables = ' -- '.join([x.ipa for x in self.syllables])
        m += 'word syllables:'.ljust(n) +  f'{syllables}\n'
        syllables = ' -- '.join([x.ipa for x in self.celex_syllables])
        m += 'celex syllables:'.ljust(n) + f'{syllables}\n'
        m += 'word n syllables:'.ljust(n) +  f'{self.n_word_syllables}\n'
        m += 'celex n syllables:'.ljust(n) + f'{self.n_celex_syllables}\n'
        m += 'word n phonemes:'.ljust(n) + f'{self.n_word_phonemes}\n'
        m += 'celex n phonemes:'.ljust(n) + f'{self.n_celex_phonemes}\n'
        m += 'Stressed syllable index:'.ljust(n) + f'{self.index}\n'
        stressed_syllable = self.stressed_syllable_based_on_index
        m += 'word syllable'.ljust(n)+f'{stressed_syllable}\n'
        m += 'celex syllable:'.ljust(n) + f'{self.stressed_celex_syllable}\n'
        return m
    

    def _handle_celex(self, celex_database = None):
        if celex_database: self.celex_database = celex_database
        else: self.celex_database = celex.Celex(word.language.language)
        self.celex_word = word_to_celex_word(self.word, self.celex_database)
        if self.celex_word:
            self.celex_syllables = self.celex_word.syllables
        else:
            self.celex_syllables = []

    def _get_stressed_syllable_based_on_index(self):
        o = get_stressed_syllable(self.word, self.celex_word, 
            self.celex_database)
        self.stressed_syllable_based_on_index, self.index, self.syllables = o 

    def _align(self):
        if not self.celex_word or not self.celex_word.ipa: 
            self.celex_ipa_simple, self.word_ipa_simple = [], []
            self.celex_phonemes, self.word_celex_phonemes = [], []
            return
        celex_ipa,word_ipa,cp,wp,o=align_celex_maus_phonemes(self.celex_word,
            self.word, self.word_phonemes)
        self.celex_ipa_simple = celex_ipa
        self.word_ipa_simple = word_ipa
        self.celex_phonemes = cp
        self.word_celex_phonemes= o

    def _get_stressed_syllable_based_on_stressed_vowel(self):
        self.stressed_syllable_based_on_vowel = None
        for phoneme in self.word_celex_phonemes:
            celex_phoneme = phoneme.celex_phoneme
            if align_phonemes.is_vowel(celex_phoneme):
                if celex_phoneme.stressed:
                    self.stressed_syllable_based_on_vowel = phoneme.syllable
                    break
        if not self.stressed_syllable_based_on_vowel and self.celex_word:
            pass
            # print('no stressed vowel found',self.word.word,self.celex_word)

    def _set_info(self):
        self.n_word_syllables = len(self.syllables)
        self.n_celex_syllables = len(self.celex_syllables)
        self.n_word_phonemes = len(self.word_phonemes)
        self.n_celex_phonemes = len(self.celex_phonemes)
        if self.celex_syllables and self.index:
            self.stressed_celex_syllable = self.celex_syllables[self.index].ipa
        else:
            self.stressed_celex_syllable= None

    def _compute_similarity_score(self):
        phonemes = self.word_celex_phonemes
        if len(phonemes) == 0:
            self.phoneme_similarity_score = 0
            return
        s = align_phonemes.compute_similarity_score_word_celex(phonemes)
        self.phoneme_similarity_score = s

    def select_best_match(self):
        self.based_on = ''
        index_syllable = self.stressed_syllable_based_on_index
        vowel_syllable = self.stressed_syllable_based_on_vowel
        if self.match:
            self.stressed_syllable = index_syllable
            self.based_on = 'index and vowel'
            return
        if not vowel_syllable and index_syllable:
            self.stressed_syllable = index_syllable
            self.based_on = 'index (no vowel syllable)'
            return
        if not index_syllable and vowel_syllable:
            self.stressed_syllable = vowel_syllable
            self.based_on = 'vowel (no index syllable)'
            return
        if not index_syllable and not vowel_syllable:
            self.stressed_syllable = None
            return
        if not self.stressed_celex_syllable:
            self.based_on = 'no stressed syllable in celex'
            self.stressed_syllable = None
            return
        self.match_vowel = compute_similarity_score_syllable(
            vowel_syllable.ipa, self.stressed_celex_syllable)
        self.match_index = compute_similarity_score_syllable(
            index_syllable.ipa,self.stressed_celex_syllable)
        if self.match_vowel > self.match_index:
            self.stressed_syllable = vowel_syllable 
            self.based_on = 'vowel'
        else:
            self.stressed_syllable = index_syllable
            self.based_on = 'index'

def compute_similarity_score_syllable(syllable1, syllable2):
    score = 0
    s1, s2 = syllable1.split(' '), syllable2.split(' ')
    s1, s2 = nw.nw(s1,s2).split('\n')
    for p1, p2 in zip(s1,s2):
        if p1 == '-' or p2 == '-': continue
        score += align_phonemes.compute_similarity_score_phoneme_pair(p1,p2) 
    print(s1,s2,score)
    return score 
        
    

  


def word_to_celex_word(word, celex_database = None):
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    if not celex_word:
        celex_word = celex_database.get_word(word.word.lower())
    return celex_word

def get_stressed_syllable(word, celex_word = None, celex_database = None):
    if not celex_database:
        celex_database = celex.Celex(word.language.language)
    syllables = list(word.syllable_set.all())
    if len(syllables) == 0:
        return None, None, syllables
    if len(syllables) == 1: 
        return syllables[0], 0, syllables
    if not celex_word:
        celex_word = word_to_celex_word(word, celex_database)
    if not celex_word: 
        # print('celex word not found', word.word)
        return None, None, syllables
    if not celex_word.syllables:
        # print('no syllables in celex word', word.word)
        return None, None, syllables
    stressed_syllable_index = celex_word.stress_list.index('primary')
    if stressed_syllable_index >= len(syllables):
        return None, None, syllables
    stressed_syllable = syllables[stressed_syllable_index]
    '''
    print(celex_word,'\n',word,'\n',
        celex_word.syllables[stressed_syllable_index], '\n',
        stressed_syllable, stressed_syllable_index)
    '''
    return stressed_syllable, stressed_syllable_index, syllables

def align_celex_maus_phonemes(celex_word, word, word_phonemes= None):
    if not word_phonemes: word_phonemes = word.phoneme_set.all()
    celex_ipa = [x[0] for x in celex_word.ipa.split(' ')]
    word_ipa = [x[0] for x in word.ipa.split(' ')]
    celex_ipa, word_ipa = nw.nw(celex_ipa,word_ipa).split('\n')
    celex_phonemes = ipa_to_instances(celex_ipa, celex_word.phonemes)
    word_phonemes = ipa_to_instances(word_ipa, word_phonemes)
    output = []
    for word_phoneme,celex_phoneme in zip(word_phonemes,celex_phonemes):
        if not word_phoneme: continue
        word_phoneme.celex_phoneme = celex_phoneme
        output.append(word_phoneme)
    return celex_ipa, word_ipa, celex_phonemes, word_phonemes, output

def ipa_to_instances(ipa, word_phonemes):
    output = []
    phoneme_index = 0
    for phoneme in ipa:
        if phoneme == '-': 
            output.append(None)
            continue
        output.append(word_phonemes[phoneme_index])
        phoneme_index += 1
    return output

def align_with_celex_word(word, celex_database = None):
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    add_celex_to_word(word, celex_word)
    celex_syllables = celex_word.syllables
    word_syllables = word.syllable_set.all()

def add_celex_to_word(word, celex_word):
    info = json.loads(word.info)
    info['celex_word'] = celex_word.line
    word.info = json.dumps(info)
    word.save()
