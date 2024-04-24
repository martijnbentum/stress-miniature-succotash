from django.db import models

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

    def __str__(self):
        m = self.identifier + ' ' + str(self.duration) 
        if self.language:
            m += ' ' + self.language.language
        return m
    

class Textgrid(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
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
    identifier = models.CharField(max_length=100, unique=True, **required)
    speaker = models.ForeignKey('Speaker',**dargs)
    phrase = models.CharField(max_length=1000)
    language = models.ForeignKey('Language',**dargs)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None, **not_required)
    end_time = models.FloatField(default=None, **not_required)

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

class Syllable(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
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

class Phoneme(models.Model):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
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

    def __str__(self):
        m = self.ipa + ' ' + self.bpcs_str 
        if self.stress:
            m += ' ' + str(self.stress)
        return m
    
class BPC(models.Model):
    bpc = models.CharField(max_length=10, default='', unique=True, **required)
    ipa = models.CharField(max_length=200, default='')
    info = models.CharField(max_length=1000, default='')

    def __str__(self):
        return self.bpc 
