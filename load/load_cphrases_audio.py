import json
from pathlib import Path
from progressbar import progressbar
from audio import audio
from utils import locations


def load_audios(audio_filenames = None):
    file_infos = make_file_infos(audio_filenames)
    n_created = 0
    for file_info in progressbar(file_infos):
        created = handle_file_info(file_info)
        if created: n_created += 1
    print('loaded',len(file_infos),'audio files')
    print('created',n_created,'new audio instances for CGN PHRASES')


def load_dataset(dataset_name = 'cgn-phrases'):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset

def load_language(language_name = 'Dutch'):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language

def handle_file_info(file_info):
    from text.models import Audio
    filename = file_info['filename']
    try: d = audio.soxinfo_to_dict(audio.soxi_info(filename))
    except: 
        print('Error with',filename)
        return False
    d['identifier'] = file_info['identifier']
    d['language'] = file_info['language']
    d['dataset'] = file_info['dataset']
    _, created = Audio.objects.get_or_create(**d)
    return created

def get_audio_filenames():
    fn = locations.cgn_phrases_audio.glob('*.wav')
    return fn

def make_file_infos(audio_filenames = None):
    if not audio_filenames:
        audio_filenames = get_audio_filenames()
    file_infos = []
    language = load_language('Dutch')
    dataset = load_dataset('cgn-phrases')
    for f in progressbar(audio_filenames):
        d = {'filename':f,'identifier':f.stem, 'language':language,
            'dataset':dataset}
        file_infos.append(d)
    return file_infos


        
