from . import locations as locations
import json
from pathlib import Path
from progressbar import progressbar
from utils import audio

def load_dataset(dataset_name):
    from text.models import Dataset
    dataset, created = Dataset.objects.get_or_create(name=dataset_name)
    return dataset

def load_langauge(language_name):
    from text.models import Language
    language = Language.objects.get(language=language_name)
    return language

def handle_audio_file(file_info, language, dataset):
    from text.models import Audio, Dataset, Language
    filename = file_info['filename']
    path = Path(filename)
    identifier = file_info['identifier']
    info = {'component':file_info['component'],'language':file_info['language']}
    d = audio.soxinfo_to_dict(audio.soxi_info(filename))
    d['identifier'] = identifier
    d['language'] = dutch
    d['info'] = json.dumps(info)
    d['dataset'] = dataset
    audio, created = Audio.objects.get_or_create(**d)
    return audio, created

def get_language_root_folder(language_name):
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        if language == language_name: return cv_root_folder
    return None

def get_audio_files(language_name):
    cv_root_folder = get_language_root_folder(language_name)
    audio_folder = locations.get_cv_path(cv_root_folder, 'clips')
    audio_files = audio_folder.glob('*.mp3')
    audio_files = [{'filename':f,'identifier':f.stem, 'language':language_name} 
        for f in audio_files]
    return audio_files

def handle_language(language_name):
    language = load_language(language_name)
    dataset = load_dataset('COMMON VOICE')
    audio_files = get_audio_files(language_name)
    for f in progressbar(files):
        _, c = handle_audio_file(f, language, dataset)
        created.append(c)
    print('created',sum(created),'new audio instance')
