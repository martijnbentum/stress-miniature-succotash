from collections import Counter
import json
import numpy as np
from utils import locations
from utils import select
from pathlib import Path
from progressbar import progressbar

def word_type_count_dict(dataset_name= 'COMMON VOICE', language_name = 'dutch',
    transcription = 'word', n_syllables = None, words = None):
    if transcription not in ['ipa', 'word']:
        m = 'transcription must be either ipa (phonemic) or word (orthographic)'
        raise ValueError(m)
    if words == None:
        words = select.select_words(dataset_name = dataset_name, 
            language_name = language_name, number_of_syllables = n_syllables)
    lemmas = [getattr(word, transcription).lower() for word in words]
    return Counter(lemmas)

def get_all_item_counts_per_language(dataset_name = 'COMMON VOICE'):
    '''prints number words syllables and phonemes per language.'''
    get_phrase_counts_per_language(dataset_name)
    get_word_counts_per_language(dataset_name)
    get_syllables_counts_per_language(dataset_name)
    get_phonemes_counts_per_language(dataset_name)

def _get_item_counts_per_language(item_type = 'word', 
    dataset_name = 'COMMON VOICE'):
    '''print the number of items of a given type in a given dataset'''
    from text.models import Language, Dataset
    if dataset_name in  ['','all',None, 'all datasets']:    
        dataset_name = 'all datasets'
        dataset = None
    else: dataset = Dataset.objects.get(name = dataset_name)
    print(f'Getting counts for {item_type} in {dataset_name}')
    d = {'dataset':dataset}
    for language in Language.objects.all():
        items = getattr(language,item_type + '_set').filter(**d)
        print(f'{language}: {items.count()}')

def get_phrase_counts_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('phrase', dataset_name)

def get_word_counts_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('word', dataset_name)

def get_syllables_counts_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('syllable', dataset_name)

def get_phonemes_counts_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('phoneme', dataset_name)

def load_cv_spk_ids(language_name):
    '''wrapper for laod_or_make_cv_spk_id_json.'''
    return load_or_make_cv_spk_id_json(language_name)

def load_or_make_cv_spk_id_json(language_name, force_make = False):
    '''make or load a json file with the speaker ids of a given language.'''
    language_name = language_name.lower()
    filename = Path(f'../{language_name}_cv_speaker_ids.json')
    if not force_make and filename.exists():
        with open(filename) as fin:
            spk_id = json.load(fin)
        return spk_id
    w = get_cv_words_of_language(language_name)
    spk_id = list(set([x.speaker_id for x in w]))
    with open(filename, 'w') as fout:
        json.dump(spk_id,fout)
    return spk_id
    
def load_or_make_all_language_spk_ids():
    from text.models import Dataset 
    languages = dataset.language_str.split(', ')
    d = {}
    for language in languages:
        print('handling',language)
        d[language] = load_or_make_cv_spk_id_json(language)
    return d

def language_n_audio_dict():
    '''return a dictionary with the number of audio files per language.'''
    if locations.language_naudios_dict.exists():
        with open(locations.language_naudios_dict) as fin:
            d = json.load(fin)
    else:
        from text.models import Language
        d = {}
        for language in Language.objects.all():
            d[language.language.lower()] = language.audio_set.all().count()
        with open(locations.language_naudios_dict, 'w') as fout:
            json.dump(d,fout)
    return d

def article_table_info_count():
    from text.models import Dataset, Language, Audio

    languages = ['Dutch','English','German','Polish','Hungarian']
    d = Dataset.objects.get(name = 'COMMON VOICE')
    for language in languages:
        print(language)
        a = Audio.objects.filter(dataset = d, language__language = language)
        audio_durations = [x.duration for x in a]
        audio_word_counts = [x.word_set.count() for x in a]
        l =  Language.objects.get(language = language)
        w = Word.objects.filter(language = l, dataset = d, n_syllables = 2)
        duration = [x.duration for x in w]
        print('audio median word count:',np.median(audio_word_counts), 
            'duration median duration:',np.median(audio_durations))
        print('words:',w.count(), 'duration:',sum(duration)/3600)
        print('-'*50)

        

