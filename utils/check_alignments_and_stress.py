from pathlib import Path
import json
from text.models import Word
from utils import select
import random

random.seed(42)

def exclude_words_without_stressed_syllable(words):
    words_with_stress = []
    for word in words:
        n = sum([int(x.stress) for x in word.syllables])
        if n == 1: words_with_stress.append(word)
    return words_with_stress


def select_words(language = 'dutch'):
    words = select.select_words(language,'COMMON VOICE',
        number_of_syllables=2,no_diphtongs=True, one_vowel_per_syllable=True,
        has_stress=True)
    return words

def sample_words(words, n = 100):
    return random.sample(words, n)

def make_word_metadata(word):
    d = {}
    d['pk'] = word.pk
    d['word'] = word.word
    d['audio_filename'] = word.audio.filename
    d['language'] = word.language.language
    d['stress_pattern'] = [int(x.stress) for x in word.syllables]
    d['stress_index'] = d['stress_pattern'].index(1)
    d['phonemes'] = [x.ipa for x in word.phonemes]
    d['start_time'] = word.start_time
    d['end_time'] = word.end_time
    return d

def make_check_dataset_filename(language_name = 'dutch', n = 100):
    directory = Path(f'../check_dataset/{language_name}/')
    if not directory.exists():
        directory.mkdir(exist_ok=True, parents=True)
    filename = directory / f'check_{language_name}_{n}.json'
    return filename

def make_all_metadata(language_name= 'dutch', words = None, save = False,
    n = 300):
    print(f'handling {n} {language_name} words')
    if not words: 
        words = select_words(language_name)
        words = exclude_words_without_stressed_syllable(words)
        words = sample_words(words, n)
    metadata = []
    for word in words:
        metadata.append(make_word_metadata(word))
    if save:
        filename = make_check_dataset_filename(language_name, n)
        with open(filename, 'w') as f:
            json.dump(metadata, f)
    return metadata

def load_metadata(language_name = 'dutch', n = 100):
    filename = make_check_dataset_filename(language_name, n)
    with open(filename,'r') as f:
        metadata = json.load(f)
    return metadata



    
    
    
    


