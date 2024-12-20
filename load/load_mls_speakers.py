import json
from load import load_mls_audio
from pathlib import Path
from progressbar import progressbar
from utils import locations

def load_meta_data(language):
    directory = locations.get_language_mls_root_folder(language)
    filename = directory / 'metadata.txt'
    with open(filename, 'r') as f:
        text = f.read().split('\n')
    header = text[0].split('\t')
    data = [line.split('\t') for line in text[1:]]
    output = []
    for line in data:
        if not line or line == ['']: continue
        d = dict(zip(header, line))
        output.append(d)
    return output

def audio_filename_to_speaker_id(filename):
    path = Path(filename)
    speaker_id = int(path.stem.split('_')[0])
    return speaker_id

def make_speaker_dict(filename):
    d = {}
    d['identifier'] = audio_filename_to_speaker_id(filename)
    d['gender'] = ''
    d['age'] = None
    return d

def add_speaker(audio, dataset):
    from text.models import Speaker
    d = make_speaker_dict(audio.filename)
    d['dataset'] = dataset
    try: speaker = Speaker.objects.get(identifier=d['identifier'])
    except Speaker.DoesNotExist: 
        Speaker.objects.create(**d)
        created = True
    else:
        created = False
        change = False
        if not speaker.age and d['age']: 
            speaker.age = d['age']
            change = True
        if not speaker.gender and d['gender']: 
            speaker.gender = d['gender']
            change = True
        if change: speaker.save()
    return created

def handle_language(language):
    from text.models import Audio
    dataset = load_mls_audio.load_dataset('MLS')
    language = load_mls_audio.load_language(language)
    audios = Audio.objects.filter(language=language, dataset=dataset)
    n_created = 0
    for audio in progressbar(audios):
        created = add_speaker(audio, dataset)
        if created: n_created += 1
    print('Added ', n_created, 'speakers, for', language)
    return n_created
        
def add_all_speakers():
    n_created = 0
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        print('handling',language,'of the common voice dataset')
        created = handle_language(language)
        n_created += created
    print('Added', n_created, 'common voice speakers in total')
    
