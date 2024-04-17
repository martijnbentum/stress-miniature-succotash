from . import locations as locations
import json
from pathlib import Path
from progressbar import progressbar
import subprocess

def cgn_audio_files(comps = 'abefghijklno',languages = ['nl','fl']):
    return locations.cgn_audio_files(comps,languages)

def soxi_info(filename):
    o = subprocess.run(['sox','--i',filename],stdout=subprocess.PIPE)
    return o.stdout.decode('utf-8')

def clock_to_duration_in_seconds(t):
    hours, minutes, seconds = t.split(':')
    s = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return s

def soxinfo_to_dict(soxinfo):
    x = soxinfo.split('\n')
    d = {}
    d['filename'] = x[1].split(': ')[-1].strip("'")
    d['n_channels'] = int(x[2].split(': ')[-1])
    d['sample_rate'] = int(x[3].split(': ')[-1])
    t = x[5].split(': ')[-1].split(' =')[0]
    d['duration'] = clock_to_duration_in_seconds(t)
    return d

def handle_audio_file(file_info):
    from text.models import Audio, Dataset, Language
    dutch = Language.objects.get(language='Dutch')
    dataset = Dataset.objects.get(name='CGN')
    filename = file_info['filename']
    path = Path(filename)
    identifier = file_info['identifier']
    info = {'component':file_info['component'],'language':file_info['language']}
    d = soxinfo_to_dict(soxi_info(filename))
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

