import json
from utils import load_cv_audio
from utils import locations
from progressbar import progressbar

age_dict = {'teens': 15, 'twenties': 25, 'thirties': 35, 'fourties': 45, 
    'fifties': 55, 'sixties': 65, 'seventies': 75, 'eighties': 85
    , 'nineties': 95}
gender_dict = {'':'','other':'other','female':'female','male':'male',
    'female_feminine':'female','male_masculine':'male'}
        

def load_validated(language_name):
    root_folder = locations.get_language_cv_root_folder(language_name)
    filename = root_folder / 'validated.tsv'
    with open(filename) as f:
        t = [line.split('\t') for line in f.read().split('\n')]
    header, data = t[0], t[1:]
    return header, data

def validated_dict(language):
    header, data = load_validated(language)
    if 'accent' in header: header[header.index('accent')] = 'accents'
    d = {}
    filename_index = header.index('path')
    for line in data:
        if len(line) != len(header): 
            print('could not parse', line)
            continue
        key = line[filename_index]
        temp = dict(zip(header,line))
        if temp['age']: temp['age'] = age_dict[temp['age']]
        temp['gender'] = gender_dict[temp['gender']]
        if 'sentence_id' in temp.keys(): del temp['sentence_id']
        d[key] = temp
    return d

def make_speaker_dict(line):
    d = {}
    d['identifier'] = line['client_id']
    del line['client_id']
    # d['info'] = json.dumps(line)
    d['gender'] = line['gender']
    d['age'] = line['age']
    if not d['age']: d['age'] = None
    return d

def add_speaker(line, dataset):
    from text.models import Speaker
    d = make_speaker_dict(line)
    d['dataset'] = dataset
    try: speaker = Speaker.objects.get(identifier=d['identifier'])
    except Speaker.DoesNotExist: 
        Speaker.objects.create(**d)
        created = True
    else:
        created = False
        change = False
        if not speaker.age: 
            speaker.age = d['age']
            change = True
        if not speaker.gender: 
            speaker.gender = d['gender']
            change = True
        if change: speaker.save()
    return created

def handle_language(language):
    dataset = load_cv_audio.load_dataset('COMMON VOICE')
    validated = validated_dict(language)
    n_created = 0
    for line in progressbar(validated.values()):
        created = add_speaker(line, dataset)
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
    
