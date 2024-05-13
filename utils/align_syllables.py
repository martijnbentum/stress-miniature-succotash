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
        self._set_info()

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
        if self.celex_syllables:
            stressed_syllable = self.celex_syllables[self.index].ipa
        else:
            stressed_syllable = 'None'
        m += 'celex syllable:'.ljust(n) + f'{stressed_syllable}\n'
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

    def _set_info(self):
        self.n_word_syllables = len(self.syllables)
        self.n_celex_syllables = len(self.celex_syllables)
        self.n_word_phonemes = len(self.word_phonemes)
        self.n_celex_phonemes = len(self.celex_phonemes)

  


def word_to_celex_word(word, celex_database = None):
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    if not celex_word:
        celex_word = celex_database.get_word(word.word.lower())
    return celex_word

def get_stressed_syllable(word, celex_word = None, celex_database = None):
    if not celex_database:
        celex_database = celex.Celex(word.language.language)
    syllables = word.syllable_set.all()
    if len(syllables) == 1: 
        print('only one syllable, it has primary stress', word.word)
        return syllables[0], 0, syllables
    if not celex_word:
        celex_word = word_to_celex_word(word, celex_database)
    if not celex_word: 
        print('celex word not found', word.word)
        return None, None, syllables
    if not celex_word.syllables:
        print('no syllables in celex word', word.word)
        return None, None, syllables
    stressed_syllable_index = celex_word.stress_list.index('primary')
    stressed_syllable = syllables[stressed_syllable_index]
    print(celex_word,'\n',word,'\n',
        celex_word.syllables[stressed_syllable_index], '\n',
        stressed_syllable, stressed_syllable_index)
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
