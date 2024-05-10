from utils import locations
from utils import maus_phoneme_mapper
from utils import phoneme_mapper
import json

class Celex:
    def __init__(self, language = 'english'):
        self.language = language.lower()
        self._set_data()
        self.phoneme_mapper = phoneme_mapper.Mapper(language)

    def _set_data(self):
        if self.language == 'english':
            self.data = open_cd(locations.celex_english_phonology_file)
            self.header = open_header('english')
        if self.language == 'dutch':
            self.data = open_cd(locations.celex_dutch_phonology_file)
            self.header = open_header('dutch')
        if self.language == 'german':
            self.data = open_cd(locations.celex_german_phonology_file)
            self.header = open_header('german')
        self._set_words()

    def _set_words(self):
        self.words = []
        self.word_dict = {}
        for line in self.data:
            word = Word(line,self)
            if not word.ok: continue
            self.words.append(word)
            self.word_dict[word.word] = word

    def get_word(self,word):
        if word not in self.word_dict: return None
        return self.word_dict[word]

class Word:
    def __init__(self, line, parent):
        self.line = line
        self.parent = parent
        self.ok = True
        self._set_info()
            

    def _set_info(self):
        for column_name, column in zip(self.parent.header, self.line):
            setattr(self,column_name, column)
        self._extract_stress_pattern()
        self._compute_n_phonemes()

    def __repr__(self):
        m = self.id_number + ' ' + self.word + ' ' + self.disc
        m += ' ' + self.cv+ ' ' + self.ipa + ' ' + self.stress_pattern
        return m

    def _extract_stress_pattern(self):
        if not hasattr(self,'disc'):
            self.ok = False
            return
        self.disc_syllables = self.disc.split('-')
        self.stress_list = []
        self.stress_pattern = ''
        for syllable in self.disc_syllables:
            if '"' in syllable:
                self.stress_list.append('secondary')
                self.stress_pattern += '2'
            elif "'" in syllable:
                self.stress_list.append('primary')
                self.stress_pattern += '1'
            else:
                self.stress_list.append('no stress')
                self.stress_pattern += '0'

    def _compute_n_phonemes(self):
        if not hasattr(self,'disc'): 
            self.ok = False
            return
        self.n_phonemes = 0
        for char in self.disc:
            if char not in ["'",'"','-']: self.n_phonemes += 1

    @property
    def cgn_syllables(self):
        if not self.ok: return
        if self.language != 'dutch': return 
        if hasattr(self,'_cgn_syllables'): return self._cgn_syllables
        return self._make_syllable_transcription('cgn')

    @property
    def baldey_syllables(self):
        if not self.ok: return
        if self.language != 'dutch': return 
        if hasattr(self,'_baldey_syllables'): return self._baldey_syllables
        return self._make_syllable_transcription('baldey')

    @property
    def arpabet_syllables(self):
        if not self.ok: return
        if self.language != 'english': return 
        if hasattr(self,'_arpabet_syllables'): return self._arpabet_syllables
        return self._make_syllable_transcription('arpabet')

    @property
    def ipa_syllables(self):
        if not self.ok: return
        if hasattr(self,'_ipa_syllables'): return self._ipa_syllables
        return self._make_syllable_transcription('ipa')

    def _make_syllable_transcription(self, phoneme_set):
        attr_name = '_' + phoneme_set + '_syllables' 
        if hasattr(self,attr_name): return getattr(self,attr_name)
        getattr(self,phoneme_set)
        transcription = getattr(self,'_' + phoneme_set)
        setattr(self,attr_name,[]) 
        syllable = []
        for phoneme in transcription:
            if phoneme == '-': 
                if syllable: getattr(self,attr_name).append(syllable)
                syllable = []
            else: syllable.append(phoneme)
        if syllable: getattr(self,attr_name).append(syllable)
        return getattr(self,attr_name)

    @property
    def syllables(self):
        if hasattr(self,'_syllables'): return self._syllables
        phoneme_index = 0
        self._syllables = []
        for syllable_index, ipa_syllable in enumerate(self.ipa_syllables):
            phonemes = []
            for phoneme in ipa_syllable:
                phonemes.append(self.phonemes[phoneme_index])
                phoneme_index += 1
            syllable = Syllable(phonemes, syllable_index, self)
            for phoneme in phonemes:
                phoneme.syllable = syllable
            self._syllables.append(syllable)
        return self._syllables

    @property
    def ipa(self):
        if not self.ok: return
        if not hasattr(self,'_ipa'): 
            disc_to_ipa = self.parent.phoneme_mapper.disc_to_ipa
            self._make_phoneme_transcription('ipa',disc_to_ipa)
        return ' '.join([p for p in self._ipa if p != '-'])

    @property
    def arpabet(self):
        if not self.ok: return
        if not hasattr(self,'_arpabet'):
            disc_to_arpabet= self.parent.phoneme_mapper.disc_to_arpabet
            self._make_phoneme_transcription('arpabet',disc_to_arpabet)
        return ' '.join([p for p in self._arpabet if p != '-'])

    @property
    def cgn(self):
        if not self.ok: return
        if not hasattr(self,'_cgn'):
            disc_to_cgn= self.parent.phoneme_mapper.disc_to_cgn
            self._make_phoneme_transcription('cgn',disc_to_cgn)
        return ' '.join([p for p in self._cgn if p != '-'])

    @property
    def baldey(self):
        if not self.ok: return
        if not hasattr(self,'_baldey'):
            disc_to_baldey= self.parent.phoneme_mapper.disc_to_baldey
            self._make_phoneme_transcription('baldey',disc_to_baldey)
        return ' '.join([p for p in self._baldey if p != '-'])

    def _make_phoneme_transcription(self,name, mapper):
        name = '_' + name
        setattr(self,name, [])
        for char in self.disc:
            if char in ['"',"'",'~',' ']: continue
            if char == '-': getattr(self,name).append( char )
            else: getattr(self,name).append( mapper[char] )

    @property
    def phonemes(self):
        if hasattr(self,'_phonemes'): return self._phonemes
        syllable_index = 0
        stressed = False
        phoneme_index = 0
        self._phonemes = []
        for p in self.disc:
            if p == '-': 
                syllable_index += 1
                stressed = False
            elif p == "'": stressed = True
            elif p in ['"','~',' ']: continue
            else:
                phoneme = Phoneme(p,'disc',phoneme_index, syllable_index,
                    self, stressed)
                self._phonemes.append(phoneme)
                phoneme_index +=1
        return self._phonemes

class Syllable:
    def __init__(self, phonemes, syllable_index, word):
        self.phonemes= phonemes 
        self.syllable_index = syllable_index
        self.word = word
        self.stress = word.stress_list[syllable_index]
        if self.stress == 'primary': self.stressed = True
        else: self.stressed = False

    def __repr__(self):
        m = self.ipa
        m += ' | ' + str(self.syllable_index) + ' | ' + self.stress
        return m

    @property
    def ipa(self):
        return ' '.join([p.ipa for p in self.phonemes])

class Phoneme:
    def __init__(self, phoneme, phoneme_set, phoneme_index, syllable_index,
        word, stressed):
        self.phoneme = phoneme
        self.phoneme_set = phoneme_set
        self.phoneme_index = phoneme_index
        self.syllable_index = syllable_index
        self.word = word
        self.stressed = stressed

    def __repr__(self):
        m = self.ipa.ljust(4) + '| ' + str(self.phoneme_index) + ' | '
        m += str(self.syllable_index) + ' | '
        m += str(self.stressed)
        return m

    @property
    def ipa(self):
        disc_to_ipa = self.word.parent.phoneme_mapper.disc_to_ipa
        return disc_to_ipa[self.phoneme]

    @property
    def arpabet(self):
        disc_to_arpabet= self.word.parent.phoneme_mapper.disc_to_arpabet
        return disc_to_arpabet[self.phoneme]

    @property
    def baldey(self):
        disc_to_baldey= self.word.parent.phoneme_mapper.disc_to_baldey
        return disc_to_baldey[self.phoneme]

    @property
    def cgn(self):
        disc_to_cng= self.word.parent.phoneme_mapper.disc_to_cgn
        return disc_to_cgn[self.phoneme]

    @property
    def disc(self):
        return self.phoneme

def get_celex_word(word, celex = None):
    language = word.language.language
    if not celex: celex = Celex(language)
    return celex.get_word(word.word)
    


def open_cd(filename):
    with open(filename) as fin:
        t = fin.read().split('\n')
    output = []
    for line in t:
        output.append(line.split('\\'))
    return output
        
def open_header(language):
    f = locations.celex_directory + language + '_header'
    with open(f) as fin:
        header = fin.read().split('\n')
    return header

class Dummy:
    def __init__(self, language ):
        self.language = 'english'
        self.header = open_header(language)
        self.phoneme_mapper = phoneme_mapper.Mapper(language)

def word_to_celex_word(word):
    info = json.loads(word.info)
    if 'celex_word' not in info.keys(): return None
    line = info['celex_word']
    language = word.language.language.lower()
    celex_word = Word(line, Dummy(language))
    return celex_word
