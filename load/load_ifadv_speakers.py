import json
from load import load_cv_audio
from utils import locations
from progressbar import progressbar

def load_ifadv_speaker_info():
    with open(locations.ifadv_speaker_info) as f:
        return json.load(f)

def add_speaker(speaker_info, dataset):
    from text.models import Speaker
    speaker_info['dataset'] = dataset
    speaker_info['info'] = json.dumps(speaker_info['line'])
    del speaker_info['line']
    try: speaker = Speaker.objects.get(identifier=speaker_info['identifier'])
    except Speaker.DoesNotExist: 
        Speaker.objects.create(**speaker_info)
        created = True
    else:
        created = False
        change = False
        if not speaker.age: 
            speaker.age = speaker_info['age']
            change = True
        if not speaker.gender: 
            speaker.gender = speaker_info['gender']
            change = True
        if change: speaker.save()
    return created

def add_all_speakers():
    dataset = load_cv_audio.load_dataset('IFADV')
    speaker_infos = load_ifadv_speaker_info()
    n_created = 0
    for speaker_info in progressbar(speaker_infos.values()):
        speaker_info = json.loads(speaker_info)
        print(speaker_info, type(speaker_info))
        created = add_speaker(speaker_info, dataset)
        if created: n_created += 1
    print('Added ', n_created, 'speakers, for IFADV')
    return n_created
        
