import json
from pathlib import Path

def get_words_per_language():
    from text.models import Language
    for language in Language.objects.all():
        print(f'{language}: {language.word_set.all().count()}')
        
def get_cv_words_of_language(language_name):
    from text.models import Language, Dataset, Word
    language = Language.objects.get(language__iexact = language_name)
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    return Word.objects.filter(language = language, dataset = dataset)

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
    
def load_or_make_all_spk_ids_cv_datset():
    from text.models import Dataset 
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    languages = dataset.language_str.split(', ')
    d = {}
    for language in languages:
        print('handling',language)
        d[language] = load_or_make_cv_spk_id_json(language)
    return d
