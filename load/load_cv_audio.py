import json
from load import load_cv_speakers 
from pathlib import Path
from progressbar import progressbar
from utils import audio
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
    filename = file_info['filename']
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


def get_audio_files(language_name):
    validated_dict = load_cv_speakers.validated_dict(language_name)
    cv_root_folder = locations.get_language_cv_root_folder(language_name)
    audio_folder = locations.get_cv_path(cv_root_folder, 'clips')
    temp= [audio_folder / k for k in validated_dict.keys()]
    audio_files = []
    for f in temp:
        if not str(f).endswith('.mp3'):
            f = Path(str(f) + '.mp3')
        audio_files.append(f)
    audio_files = [{'filename':f,'identifier':f.stem, 'language':language_name} 
        for f in audio_files]
    return audio_files

def handle_language(language_name):
    print('handling',language_name,'of the common voice dataset')
    language = load_language(language_name)
    dataset = load_dataset('COMMON VOICE')
    audio_files = get_audio_files(language_name)
    n_created = 0
    for f in progressbar(audio_files):
        created = handle_audio_file(f, language, dataset)
        if created: n_created += 1
    print('created',n_created,'new audio instances for',language_name)

def handle_all_languages():
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        handle_language(language)

