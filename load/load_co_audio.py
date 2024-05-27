import json
from pathlib import Path
from progressbar import progressbar
from audio import audio
from utils import locations

def load_dataset(dataset_name = 'COOLEST'):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset

def load_language(language_name = 'dutch'):
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


def get_audio_files():
    audio_folder = locations.coolest_audio
    audio_files = audio_folder.glob('**/*.wav')
    audio_files = [{'filename':f,'identifier':f.stem, 'language':'dutch'} 
        for f in audio_files]
    return audio_files

def handle_all_audio_files():
    print('loading audio files of the coolest dataset')
    language = load_language()
    dataset = load_dataset()
    audio_files = get_audio_files()
    n_created = 0
    for f in progressbar(audio_files):
        created = handle_audio_file(f, language, dataset)
        if created: n_created += 1
    print('created',n_created,'new audio instances for coolest dataset')


