import json
from load import load_mls_speakers 
from pathlib import Path
from progressbar import progressbar
from audio import audio
from utils import locations

def load_dataset(dataset_name):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset

def load_language(language_name):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language

def handle_audio_file(file_info, language, dataset):
    from text.models import Audio, Dataset, Language
    filename = str(file_info['filename'])
    path = Path(filename)
    identifier = file_info['identifier']
    try: d = audio.soxinfo_to_dict(audio.soxi_info(filename))
    except: 
        print('Error with',filename)
        return False
    d['identifier'] = identifier
    d['language'] = language
    d['dataset'] = dataset
    _, created = Audio.objects.get_or_create(**d)
    return created


def get_audio_files(language_name, 
    splits=['train','dev','test']):
    mls_root_folder = locations.get_language_mls_root_folder(language_name)
    audio_folder = locations.get_mls_path(mls_root_folder, 'audio')
    audio_files = []
    for split in splits:
        directory = audio_folder / split
        fn = directory.glob('*.wav')
        audio_files.extend(fn)
    audio_files = [{'filename':str(f),'identifier':f.stem, 
        'language':language_name} 
        for f in audio_files]
    return audio_files

def handle_language(language_name, 
    splits = ['train','dev','test']):
    print('handling',language_name,'of the multilingual librispeech dataset',
    'splits',splits)
    language = load_language(language_name)
    dataset = load_dataset('MLS')
    print(f'handling {language}, {dataset}')
    audio_files = get_audio_files(language_name, splits)
    n_created = 0
    for f in progressbar(audio_files):
        created = handle_audio_file(f, language, dataset)
        if created: n_created += 1
    print('created',n_created,'new audio instances for',language_name)

def handle_all_languages():
    for mls_root_folder in locations.mls_root_folders:
        language = mls_root_folder.stem.split('_')[-1].lower()
        handle_language(language)

