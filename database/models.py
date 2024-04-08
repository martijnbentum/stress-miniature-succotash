from django.db import models

# Create your models here.

class Language:
    language = models.CharField(max_length=100)

class Dataset:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    language = models.ForeignKey('Language',**dargs)

class Audio:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    filename = models.CharField(max_length=300)
    sample_rate = models.IntegerField(default=None)
    n_channels = models.IntegerField(default=None)

class Phrase:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    phrase = models.CharField(max_length=1000)
    language = models.ForeignKey('Language',**dargs)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)

class Word:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    dataset = models.ForeignKey('Dataset',**dargs)
    phrase = models.ForeignKey('Phrase',**dargs)
    index = models.IntegerField(default=None)
    word = models.CharField(max_length=100)
    ipa = models.CharField(max_length=100)
    language = models.ForeignKey('Language',**dargs)
    isolation = models.BooleanField(default=None)
    n_syllables = models.IntegerField(default=None)
    n_phonemes = models.IntegerField(default=None)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)

class Syllable:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    word = models.ForeignKey('Word',**dargs)
    ipa = models.CharField(max_length=100)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)

class Phoneme:
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    word = models.ForeignKey('Word',**dargs)
    word_index = models.IntegerField(default=None)
    syllable = models.ForeignKey('Syllable',**dargs)
    syllable_index = models.IntegerField(default=None)
    ipa = models.CharField(max_length=10)
    stress = models.BooleanField(default=None)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None)
    end_time = models.FloatField(default=None)
    bpc = models.CharField(max_length=30)
    
