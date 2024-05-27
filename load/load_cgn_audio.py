import json
from pathlib import Path
from progressbar import progressbar
from utils import locations 
from audio import audio

def cgn_audio_files(comps = 'abefghijklno',languages = ['nl','fl']):
    return locations.cgn_audio_files(comps,languages)

def handle_audio_file(file_info):
    from text.models import Audio, Dataset, Language
    dutch = Language.objects.get(language='Dutch')
    dataset = Dataset.objects.get(name='CGN')
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

def handle_audio_files(files = None):
    if not files: files = cgn_audio_files()
    print('handling',len(files),'audio files')
    created = []
    for f in progressbar(files):
        _, c = handle_audio_file(f)
        created.append(c)
    print('created',sum(created),'new audio instance')

