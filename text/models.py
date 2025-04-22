from django.db import models
import json
import numpy as np

# Create your models here.
required = {'blank':False,'null':False}
not_required = {'blank':True,'null':True}

class Language(models.Model):
    language = models.CharField(max_length=100, unique=True, **required)
    iso = models.CharField(max_length=10, default='')

    def __str__(self):
        return self.language + ' ' + self.iso

class Dataset(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    name = models.CharField(max_length=100, unique=True, **required)
    description = models.CharField(max_length=1000)
    languages = models.ManyToManyField('Language', blank=True, default=None)

    def __str__(self):
        m = self.name + ' ' + self.language_str
        return m

    @property
    def language_str(self):
        if not self.languages:
            return ''
        return ', '.join([l.language for l in self.languages.all()])

class Audio(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    identifier = models.CharField(max_length=100, unique=True, **required)
    filename = models.CharField(max_length=300, **required)
    sample_rate = models.IntegerField(default=None)
    n_channels = models.IntegerField(default=None)
    duration = models.FloatField(default=None)
    info = models.CharField(max_length=1000, default='')
    language = models.ForeignKey('Language',**dargs)
    dataset = models.ForeignKey('Dataset',**dargs)
    hidden_state = models.IntegerField(default=None, null = True)
    hidden_state_model = models.TextField(blank=True, null=True)

    def __str__(self):
        m = self.identifier + ' ' + str(self.duration) 
        if self.language:
            m += ' ' + self.language.language
        return m
    

class Textgrid(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    identifier = models.CharField(max_length=100, unique=True, **required)
    audio = models.ForeignKey('Audio',**dargs)
    filename = models.CharField(max_length=300, **required)
    table_filename = models.CharField(max_length=300, default='')
    phoneme_set_name = models.CharField(max_length=30, default='')
    speakers = models.ManyToManyField('Speaker', blank=True, default=None)
    n_speakers = models.IntegerField(default=None, **not_required)

    def __str__(self):
        return self.identifier + ' ' + self.phoneme_set_name

    def load(self):
        import textgrids
        return textgrids.TextGrid(self.filename)

class Phrase(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    identifier = models.CharField(max_length=100, unique=True, **required)
    speaker = models.ForeignKey('Speaker',**dargs)
    phrase = models.TextField(blank=True, null=True)
    ipa = models.TextField(blank=True, null=True)
    index = models.IntegerField(default=None, **not_required)
    language = models.ForeignKey('Language',**dargs)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None, **not_required)
    end_time = models.FloatField(default=None, **not_required)

    def __str__(self):
        phrase = self.phrase 
        if len(phrase) > 64: phrase = phrase[:60] + ' ...'
        return phrase

    @property
    def words(self):
        if not hasattr(self,'_words'):
            self._words = list(self.word_set.all())
        return self._words

    @property
    def syllables(self):
        if not hasattr(self,'_syllables'):
            self._syllables = []
            for word in self.words:
                self._syllables += word.syllables
        return self._syllables

    @property
    def phonemes(self):
        if not hasattr(self,'_phonemes'):
            self._phonemes = []
            for word in self.words:
                self._phonemes += word.phonemes
        return self._phonemes

    @property
    def audio_signal(self):
        signal, sr = audio.load_audio(self.audio)
        signal = item_to_samples(self, signal, sr)
        return signal, sr

class Speaker(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    identifier = models.CharField(max_length=100, unique=True, **required)
    name = models.CharField(max_length=100)
    birth_year = models.IntegerField(default=None, **not_required)
    age = models.IntegerField(default=None, **not_required)
    gender = models.CharField(max_length=10, default='')
    info = models.CharField(max_length=1000, default='')
    dataset = models.ForeignKey('Dataset',**dargs)

    def __str__(self):
        identifier = self.identifier
        if len(identifier) > 9: identifier = identifier[:9] + '...'
        return identifier+ ' ' + self.gender + ' ' + str(self.age)

    @property
    def info_dict(self):
        return json.loads(self.info)

    @property
    def accent(self):
        if 'accent' in self.info_dict:
            return self.info_dict['accent']

class Word(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    identifier = models.CharField(max_length=100, unique=True, **required)
    speaker = models.ForeignKey('Speaker',**dargs)
    phrase = models.ForeignKey('Phrase',**dargs)
    index = models.IntegerField(default=None, **not_required)
    word = models.CharField(max_length=100, **required)
    ipa = models.CharField(max_length=100)
    language = models.ForeignKey('Language',**dargs)
    isolation = models.BooleanField(default=None, **not_required)
    overlap = models.BooleanField(default=None, **not_required)
    n_syllables = models.IntegerField(default=None, **not_required)
    n_phonemes = models.IntegerField(default=None, **not_required)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)
    info = models.CharField(max_length=1000, default='')

    def __str__(self):
        return self.word + ' ' + self.ipa 

    @property
    def info_dict(self):
        return json.loads(self.info)

    @property
    def accent(self):
        if 'accent' in self.info_dict:
            return self.info_dict['accent']

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def phrase_words(self):
        if not hasattr(self,'_phrase_words'):
            self._phrase_words = list(self.phrase.word_set.all())
        return self._phrase_words

    @property
    def next_word(self):
        if self.index == self.n_words - 1: return None
        return self.phrase_words[self.index + 1]

    @property
    def previous_word(self):
        if self.index == 0: return None
        return self.phrase_words[self.index - 1]

    @property
    def phonemes(self):
        if not hasattr(self,'_phonemes'):
            self._phonemes = list(self.phoneme_set.all())
        return self._phonemes

    @property
    def syllables(self):
        if not hasattr(self,'_syllables'):
            self._syllables = list(self.syllable_set.all())
        return self._syllables

    @property
    def audio_signal(self):
        signal, sr = audio.load_audio(self.audio)
        signal = item_to_samples(self, signal, sr)
        return signal, sr

    def hidden_state_frames(self, model_name = 'pretrained-xlsr'):
        from utils import load_hidden_states as lhs
        frames = lhs.load_word_hidden_state_frames(self, 
            model_name = model_name)
        return frames

    def hidden_states(self, model_name = 'pretrained-xlsr'):
        frames = self.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        if not hasattr(frames,'outputs'): return None
        hidden_states = frames.outputs
        return hidden_states

    def cnn(self, mean = False, model_name = 'pretrained-xlsr',
        percentage_overlap = None, middle_frame = False):
        frames = self.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        cnn = frames.cnn(start_time = self.start_time, end_time = self.end_time,
            percentage_overlap = percentage_overlap, 
            middle_frame = middle_frame,
            average = mean)
        return cnn

    def transformer(self, layer = 1, mean = False, 
        model_name = 'pretrained-xlsr'):
        frames = self.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        transformer = frames.transformer(layer, start_time = self.start_time,
            end_time = self.end_time, average = mean, 
            percentage_overlap = percentage_overlap,
            middle_frame = middle_frame)
        return transformer

    def codebook_indices(self, model_name = 'pretrained-xlsr'):
        from utils import load_codevectors as lc
        return lc.load_word_codebook_indices(self, model_name = model_name)

    def codevectors(self, mean = False, model_name = 'pretrained-xlsr',
        codebook = None):
        from utils import load_codevectors as lc
        return lc.load_word_codevectors(self, model_name = model_name,
            codebook = codebook)

class Syllable(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    identifier = models.CharField(max_length=100, unique=True, **required)
    word = models.ForeignKey('Word',**dargs)
    phoneme_str= models.CharField(max_length=100,default='') 
    ipa = models.CharField(max_length=100, default='')
    index = models.IntegerField(default=None)
    stress = models.BooleanField(default=None, **not_required)
    audio = models.ForeignKey('Audio',**dargs)
    speaker = models.ForeignKey('Speaker',**dargs)
    language= models.ForeignKey('Language',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)

    def __str__(self):
        m = self.ipa 
        if self.stress != None: m += ' ' + str(self.stress)
        return m

    @property
    def onset(self):
        if hasattr(self,'_onset'): return self._onset
        if not self.vowel: 
            if self.phonemes[0].is_consonant:
                self._onset = [self.phonemes[0]]
            else: self._onset = []
            return self._onset
        vowel_index = self.vowel[0].syllable_index
        if vowel_index == 0: self._onset = []
        else: self._onset = self.phonemes[:vowel_index]
        return self._onset

    @property
    def vowel(self):
        if not hasattr(self,'_vowel'):
            self._vowel = list(self.phoneme_set.filter(
                bpcs_str__contains='vowel'))
        return self._vowel

    @property
    def rime(self):
        if hasattr(self,'_rime'): return self._rime
        if not self.vowel: 
            self._rhyme = []
            return self._rhyme
        vowel_index = self.vowel[0].syllable_index
        if vowel_index == 0: self._rime = self.phonemes
        else: self._rime = self.phonemes[vowel_index:]
        return self._rime

    @property
    def coda(self):
        if hasattr(self,'_coda'): return self._coda
        if not self.vowel: 
            if self.phonemes[-1].is_consonant:
                self._coda = [self.phonemes[-1]]
            else: self._coda = []
            return self._coda
        vowel_index = self.vowel[-1].syllable_index
        if vowel_index == len(self.phonemes) - 1: self._coda = []
        else: self._coda = self.phonemes[vowel_index+1:]
        return self._coda

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def word_syllables(self):
        return word.syllables

    @property
    def phonemes(self):
        if not hasattr(self,'_phonemes'):
            self._phonemes = list(self.phoneme_set.all())
        return self._phonemes

    @property
    def next_syllable(self):
        if self.index == self.n_syllables - 1: return None
        return self.word_syllables[self.index + 1]

    @property
    def previous_syllable(self):
        if self.index == 0: return None
        return self.word_syllables[self.index - 1]

    @property
    def audio_signal(self):
        signal, sr = audio.load_audio(self.audio)
        signal = item_to_samples(self, signal, sr)
        return signal, sr


    def cnn(self, mean = False, model_name = 'pretrained-xlsr',
        percentage_overlap = None, middle_frame = False):
        frames = self.word.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        cnn = frames.cnn(start_time = self.start_time, end_time = self.end_time,
            percentage_overlap = percentage_overlap, 
            middle_frame = middle_frame,
            average = mean)
        return cnn

    def transformer(self, layer = 1, mean = False, 
        model_name = 'pretrained-xlsr'):
        frames = self.word.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        transformer = frames.transformer(layer, start_time = self.start_time,
            end_time = self.end_time, average = mean, 
            percentage_overlap = percentage_overlap,
            middle_frame = middle_frame)
        return transformer

    def codebook_indices(self, model_name = 'pretrained-xlsr'):
        from utils import load_codevectors as lc
        return lc.load_syllable_codevectors(self, 
            return_codebook_indices = True, model_name = model_name)

    def codevectors(self, mean = False, model_name = 'pretrained-xlsr',
        codebook = None):
        from utils import load_codevectors as lc
        cv = lc.load_syllable_codevectors(self, codebook = codebook,
            model_name = model_name)
        if cv is None: return None
        if mean: return np.mean(cv, axis = 0)
        return cv

class Phoneme(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    identifier = models.CharField(max_length=100, unique=True, **required)
    phoneme = models.CharField(max_length=5, default='')
    word = models.ForeignKey('Word',**dargs)
    word_index = models.IntegerField(default=None)
    syllable = models.ForeignKey('Syllable',**dargs)
    syllable_index = models.IntegerField(default=None, **not_required)
    ipa = models.CharField(max_length=5, default='')
    stress = models.BooleanField(default=None, **not_required)
    audio = models.ForeignKey('Audio',**dargs)
    speaker = models.ForeignKey('Speaker',**dargs)
    language= models.ForeignKey('Language',**dargs)
    start_time = models.FloatField(default=None, **not_required)
    end_time = models.FloatField(default=None, **not_required)
    bpcs = models.ManyToManyField('BPC',blank=True, default=None)
    bpcs_str = models.CharField(max_length=100, default='')
    _f0 = models.CharField(max_length=300, default='')
    _f1 = models.CharField(max_length=300, default='')
    _f2 = models.CharField(max_length=300, default='')
    _spectral_tilt = models.CharField(max_length=100, default='')
    intensity = models.FloatField(default=None, **not_required)

    def __str__(self):
        m = self.ipa + ' ' + self.bpcs_str 
        if self.stress != None:
            m += ' ' + str(self.stress)
        return m

    @property
    def index_of_syllable(self):
        return self.syllable_index

    @property
    def is_vowel(self):
        return 'vowel' in self.bpcs_str

    @property
    def is_consonant(self):
        return 'consonant' in self.bpcs_str

    @property
    def simple_ipa(self):
        if not self.ipa: return ''
        return self.ipa[0]

    @property
    def word_phonemes(self):
        return self.word.phonemes

    @property
    def previous_phoneme(self):
        if self.index == 0: return None
        return self.word_phonemes[self.word_index - 1]

    @property
    def next_phoneme(self):
        if self.index == self.n_phonemes - 1: return None
        return self.word_phonemes[self.word_index + 1]

    @property
    def f0(self):
        if not self._f0: return []
        return json.loads(self._f0)

    @property
    def f1(self):
        if not self._f1: return []
        return json.loads(self._f1)
    
    @property
    def f2(self):
        if not self._f2: return []
        return json.loads(self._f2)
    
    @property
    def spectral_tilt(self):
        if not self._spectral_tilt: return []
        return json.loads(self._spectral_tilt)

    @property
    def acoustic_features(self):
        d = {'f0':self.f0,'f1':self.f1,'f2':self.f2,
                'spectral_tilt':self.spectral_tilt,'intensity':self.intensity}
        return d

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def audio_signal(self):
        signal, sr = audio.load_audio(self.audio)
        signal = item_to_samples(self, signal, sr)
        return signal, sr

    def cnn(self, mean = False, model_name = 'pretrained-xlsr',
        percentage_overlap = None, middle_frame = False):
        frames = self.word.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        cnn = frames.cnn(start_time = self.start_time, end_time = self.end_time,
            percentage_overlap = percentage_overlap, 
            middle_frame = middle_frame,
            average = mean)
        return cnn

    def transformer(self, layer = 1, mean = False, 
        model_name = 'pretrained-xlsr'):
        frames = self.word.hidden_state_frames(model_name = model_name)
        if frames is None: return None
        transformer = frames.transformer(layer, start_time = self.start_time,
            end_time = self.end_time, average = mean, 
            percentage_overlap = percentage_overlap,
            middle_frame = middle_frame)
        return transformer

    def codebook_indices(self, model_name = 'pretrained-xlsr'):
        from utils import load_codevectors as lc
        return lc.load_phoneme_codevectors(self, 
            return_codebook_indices = True, model_name = model_name)

    def codevectors(self, mean = False, model_name = 'pretrained-xlsr',
        codebook = None):
        from utils import load_codevectors as lc
        cv = lc.load_phoneme_codevectors(self, codebook = codebook,
            model_name = model_name)
        if cv is None: return None
        if mean: return np.mean(cv, axis = 0)
        return cv

    
class BPC(models.Model):
    bpc = models.CharField(max_length=10, default='', unique=True, **required)
    ipa = models.CharField(max_length=200, default='')
    info = models.CharField(max_length=1000, default='')

    def __str__(self):
        return self.bpc 
