import json
from utils import locations 
import pandas as pd
from progressbar import progressbar

gender = {1:'male',2:'female'}
language = {'DU':'Dutch', 'EN':'English', 'FR':'French', 'GE':'German', 
    'IN':'India', 'ES':'Spanish', 'RU':'Russian', 'KU':'Kurdish',
    'AKAN':'Ghana', 'IBO':'Nigeria', 'PO':'Polish', 'AR':'Arabic',
    'xxx':None, '-':None, '':None, ' ':None}
region = {'regV1': 'Antwerp', 'regV2': 'East-Flanders', 
    'regV3': 'West-Flanders', 'regV4': 'Limburg', 'regV5': 'Vlaams-Brabant',
    'regV6': 'Brussels', 'regW': 'Wallony', 'regZ': 'Outside Belgium'} 
place = {'NL':'Netherlands', 'FR':'France', 'DE':'Germany',
    'GB':'Great Britain', 'US':'United States', 'IN':'India', 
    'CH':'Switzerland', 'RU':'Russia', 'RO':'Romania', 'NG':'Nigeria', 
    'NO':'Norway', 'PT':'Portugal', '-': None, 'xxx':None, '':None, ' ':None,}

def open_file(filename):
    wb = pd.read_excel(filename)
    data = wb.values.tolist()
    header = wb.columns.values.tolist()
    return header, data

def speaker_info(line, header):
    d = {}
    for i, h in enumerate(header):
        v = line[i]
        h = h.lower()
        if h == 'sex':
            d[h] = gender[v] if v in gender else None
        elif 'date' in h:
            try: d[h] = v.year
            except AttributeError: 
                print('date error', v)
                d[h] = None
        elif h == 'mothertongue':
            d[h] = language[v] if v in language else None
        elif h == 'fathertongue':
            d[h] = language[v] if v in language else None
        elif 'region' in h:
            d[h] = region[v] if v in region else None
        elif 'place' in h:
            d[h] = place[v] if v in place else v
        else:
            d[h] = line[i]
    if d['birthdate']:
        if d['dateavi']:
            d['age'] = d['dateavi'] - d['birthdate']
        else:
            d['age'] = 2005 - d['birthdate']
    else:
        d['age'] = None
    return d

def make_speaker_dict(line, header):
    d = {}
    info = speaker_info(line, header)
    d['info'] = json.dumps(info)
    d['identifier'] = info['childid']
    if d['identifier'] == 'S01CO53V3':
        d['identifier'] = 'S01C053V3'
    if d['identifier'] == 'S01CO54V3':
        d['identifier'] = 'S01C054V3'
    if d['identifier'] == 'S04C069V4':
        d['identifier'] = 'S04C069M4'
    d['gender'] = info['sex']
    birth_year = info['birthdate']
    d['age'] = info['age']
    return d

def add_speaker(line,header):
    from text.models import Speaker
    d = make_speaker_dict(line,header)
    speaker, created = Speaker.objects.get_or_create(**d)
    return created

def add_all_speakers():
    for f in locations.chorec_speaker_info_files:
        header, data = open_file(f)
        print('reading speaker data', len(data), 'speakers in total.')
        n_created = 0
        for line in progressbar(data):
            created = add_speaker(line,header)
            if created: n_created += 1
        print('Added ', n_created, 'speakers.')
