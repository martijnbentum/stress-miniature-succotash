import json
from pathlib import Path

def get_all_items_per_language(dataset_name = 'COMMON VOICE'):
    get_words_per_language(dataset_name)
    get_syllables_per_language(dataset_name)
    get_phonemes_per_language(dataset_name)


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

def get_words_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('word', dataset_name)

def get_syllables_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('syllable', dataset_name)

def get_phonemes_per_language(dataset_name = 'COMMON VOICE'):
    _get_item_counts_per_language('phoneme', dataset_name)

def _get_cv_items_of_language(language_name, item_type = 'word'):
    from text.models import Language, Dataset, Word, Syllable, Phoneme
    language = Language.objects.get(language__iexact = language_name)
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    if item_type == 'word': Item = Word
    if item_type == 'syllable': Item = Syllable
    if item_type == 'phoneme': Item = Phoneme
    return Item.objects.filter(language = language, dataset = dataset)
        
def get_cv_words_of_language(language_name):
    return _get_cv_items_of_language(language_name, 'word')
        
def get_cv_syllable_of_language(language_name):
    return _get_cv_items_of_language(language_name, 'syllable')

def get_cv_phoneme_of_language(language_name):
    return _get_cv_items_of_language(language_name, 'phoneme')

def load_cv_spk_ids(language_name):
    with open(f'../{language_name}_cv_speaker_ids.json') as fin:
        spk_ids = json.load(fin)
    return spk_ids

def load_or_make_cv_spk_id_json(language_name, force_make = False):
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
    
def load_or_make_all_spk_ids_cv_dataset():
    from text.models import Dataset 
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    languages = dataset.language_str.split(', ')
    d = {}
    for language in languages:
        print('handling',language)
        d[language] = load_or_make_cv_spk_id_json(language)
    return d
