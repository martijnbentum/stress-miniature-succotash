import json
from load import load_cv_audio
from utils import locations
from progressbar import progressbar

def get_speaker_identifiers():
    folders = [x for x in locations.coolest_audio.iterdir() if x.is_dir()]
    output = []
    for path in locations.coolest_audio.iterdir():
        if not path.is_dir(): continue
        if path.stem.startswith('.'): continue
        output.append('coolest_' +path.stem)
    return output

        
'''
    identifier = models.CharField(max_length=100, unique=True, **required)
    name = models.CharField(max_length=100)
    birth_year = models.IntegerField(default=None, **not_required)
    age = models.IntegerField(default=None, **not_required)
    gender = models.CharField(max_length=10, default='')
    info = models.CharField(max_length=1000, default='')
    dataset = models.ForeignKey('Dataset',**dargs)
'''

def make_speaker_dict(identifier, dataset, age = None, gender = None, 
    info = None):
    d = {}
    d['identifier'] = identifier
    d['dataset'] = dataset
    if age: d['age'] = age
    if gender: d['gender'] = gender
    if info: d['info'] = info
    return d

def add_speaker(speaker_dict):
    from text.models import Speaker
    d = speaker_dict
    try: speaker = Speaker.objects.get(identifier=d['identifier'])
    except Speaker.DoesNotExist: 
        Speaker.objects.create(**d)
        created = True
    else:
        created = False
        change = False
        if 'age' in d and not speaker.age:
            speaker.age = d['age']
            change = True
        if 'gender' in d and not speaker.gender:
            speaker.gender = d['gender']
            change = True
        if 'info' in d and not speaker.info:
            speaker.info = d['info']
            change = True
        if change: speaker.save()
    return created

        
def add_all_speakers():
    from text.models import Dataset
    speaker_identifiers = get_speaker_identifiers()
    dataset = Dataset.objects.get(name='COOLEST')
    n_created = 0
    for identifier in speaker_identifiers:
        speaker_dict = make_speaker_dict(identifier,dataset)
        created = add_speaker(speaker_dict)
        n_created += created
    print('Added', n_created, 'common voice speakers in total')
    
