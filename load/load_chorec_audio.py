import json
from pathlib import Path
from progressbar import progressbar
from utils import locations 
from audio import audio

def chorec_audio_files():
    return list(locations.chorec_audio_files)

def filename_to_file_info(filename):
    d = {}
    path = Path(filename)
    filename = str(filename)
    d['component'] = 'AVI read aloud sentences'
    d['filename'] = filename
    d['identifier'] = path.stem
    d['language'] = 'flemish dutch'
    return d

def handle_audio_file(filename):
    from text.models import Audio, Dataset, Language
    dutch = Language.objects.get(language='Dutch')
    dataset = Dataset.objects.get(name='CHOREC')
    file_info = filename_to_file_info(filename)
    filename = file_info['filename']
    path = Path(filename)
    identifier = file_info['identifier']
    info = {'component':file_info['component'],'language':file_info['language']}
    d = audio.soxinfo_to_dict(audio.soxi_info(filename))
    d['identifier'] = identifier
    d['language'] = dutch
    d['info'] = json.dumps(info)
    d['dataset'] = dataset
    a, created = Audio.objects.get_or_create(**d)
    return a, created

def handle_audio_files(files = None):
    if not files: files = chorec_audio_files()
    print('handling',len(files),'audio files')
    created = []
    for f in progressbar(files):
        _, c = handle_audio_file(f)
        created.append(c)
    print('created',sum(created),'new audio instance')


def handle_component(comp = 'o', languages = ['nl']):
    files = cgn_audio_files(comps = comp, languages = languages)
    handle_audio_files(files)
