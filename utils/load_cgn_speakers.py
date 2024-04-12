import json
from . import locations_pony as locations
from progressbar import progressbar

gender = {'sex1':'male','sex2':'female','sexX':'unknown'}

def open_file():
    t = locations.cgn_speaker_file.open().read().split('\n')
    header = t[0].split('\t')
    data = [x.split('\t') for x in t[1:] if x]
    return header, data

def speaker_info(line, header):
    d = {}
    for i, h in enumerate(header):
        d[h] = line[i]
    return d

def make_speaker_dict(line, header):
    d = {}
    d['info'] = json.dumps(speaker_info(line, header))
    d['identifier'] = line[4]
    d['gender'] = gender[line[5]]
    try:birth_year = int(line[6])
    except ValueError: birth_year = None
    d['birth_year'] = birth_year
    if birth_year: d['age'] = 2000 - birth_year
    else: d['age'] = None
    return d

def add_speaker(line,header):
    from text.models import Speaker
    d = make_speaker_dict(line,header)
    speaker, created = Speaker.objects.get_or_create(**d)
    return created

def add_all_speakers():
    header, data = open_file()
    print('reading speaker data', len(data), 'speakers in total.')
    n_created = 0
    for line in progressbar(data):
        created = add_speaker(line,header)
        if created: n_created += 1
    print('Added ', n_created, 'speakers.')
