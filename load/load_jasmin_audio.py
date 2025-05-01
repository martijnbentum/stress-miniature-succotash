import json
from pathlib import Path
from progressbar import progressbar
from utils import locations 
from audio import audio

def jasmin_audio_files():
    o =locations.jasmin_comp_p_audio_files + locations.jasmin_comp_q_audio_files
    return o

def filename_to_file_info(filename):
    d = {}
    path = Path(filename)
    filename = str(filename)
    if 'comp-p' in filename:
        d['component'] = 'comp-p'
    elif 'comp-q' in filename:
        d['component'] = 'comp-q'
    else:
        raise ValueError('no component found in',filename)
    d['filename'] = filename
    d['identifier'] = path.stem
    if 'nl' in filename:
        d['language'] = 'netherlandic dutch'
    elif 'vl' in filename:
        d['language'] = 'flemish dutch'
    else:
        raise ValueError('no language found in',filename)
    return d

def handle_audio_file(filename):
    from text.models import Audio, Dataset, Language
    dutch = Language.objects.get(language='Dutch')
    dataset = Dataset.objects.get(name='JASMIN')
    file_info = filename_to_file_info(filename)
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
    if not files: files = jasmin_audio_files()
    print('handling',len(files),'audio files')
    created = []
    for f in progressbar(files):
        _, c = handle_audio_file(f)
        created.append(c)
    print('created',sum(created),'new audio instance')


