import json
from utils import locations 
from progressbar import progressbar



def open_dutch_file():
    with open(locations.jasmin_dutch_speaker_file) as f:
        t = f.read().split('\n')
    header = t[0].split('\t')
    data = [x.split('\t') for x in t[1:] if x]
    return header, data

def open_flemish_file():
    with open(locations.jasmin_flemish_speaker_file) as f:
        t = f.read().split('\n')
    header = t[0].split('\t')
    data = [x.split('\t') for x in t[1:] if x]
    return header, data

def load_speaker_files():
    dutch_header, dutch_data = open_dutch_file()
    flemish_header, flemish_data = open_flemish_file()
    if not dutch_header == flemish_header: 
        raise ValueError('Headers of Dutch and Flemish speaker files do not match')
    header = dutch_header
    data = dutch_data + flemish_data
    return header, data

def speaker_info(line, header):
    d = {}
    for i, h in enumerate(header):
        h = h.lower()
        if i >= len(line): continue
        d[h] = line[i]
        if h == 'age':
            try: d[h] = int(line[i])
            except ValueError: d[h] = None
        if h == 'group':
            n = int(line[i]) 
            d[h] = group[n]
            d['simple_group'] = simple_group[n]
        if h == 'gender':
            d[h] = gender[line[i]]
        if h == 'dialectregion':
            d['dialect_code'] = line[i]
            if not line[i]: 
                d[h] = ''
                d['dialect_general_region'] = ''
            else:
                d[h] = dialect_codes[line[i]]
                if 'N' in line[i]:
                    d['dialect_general_region'] = dialect_codes[line[i][1]]
                else:
                    d['dialect_general_region'] = dialect_codes[line[i]]
        if h == 'birthplace':
            if 'N-' in line[i]:
                d['birthplace'] = 'Netherlands'
            elif 'B-' in line[i]:
                d['birthplace'] = 'Belgium'
            else:
                d['birthplace'] = country_dict()[line[i]]
            d['birthplace_code'] = line[i]
        ld = language_dict()
        if h == 'homelanguage1':
            d['homelanguage1'] = ld[line[i]] if line[i] in ld else ''
            d['homelanguage1_code'] = line[i]
        if h == 'homelanguage2':
            d['homelanguage2'] = ld[line[i]] if line[i] in ld else '' 
            d['homelanguage1_code'] = line[i]
        if h == 'eduplace':
            if 'N-' in line[i]:
                d['birthplace'] = 'Netherlands'
            elif 'B-' in line[i]:
                d['birthplace'] = 'Belgium'
            else:
                d['eduplace'] = country_dict()[line[i]]
            d['eduplace_code'] = line[i]
        if h == 'edulevel':
            if not line[i]:
                d['edulevel'] = ''
            else:
                d['edulevel'] = education[line[i]]
        if h == 'comment':
            if not line[i]:
                d['comment'] = ''
            else:
                d['comment'] = comment[line[i]]
    return d

def make_speaker_dict(line, header):
    d = {}
    info = speaker_info(line, header)
    d['info'] = json.dumps(info)
    d['identifier'] = info['regionspeaker']
    d['gender'] = info['gender']
    d['birth_year'] = 2007 - info['age']
    d['age'] = info['age']
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


def language_dict():
    with open(locations.jasmin_languages_file, encoding = 'ISO8859') as f:
        d = f.read().split('\n')
    d = dict([x.split('\t') for x in d if x and len(x.split('\t')) == 2])
    d['dut'] = 'Dutch'
    return d

def country_dict():
    with open(locations.jasmin_countries_file, encoding = 'ISO8859') as f:
        d = f.read().split('\n')
    d = dict([x.split('\t') for x in d if x and len(x.split('\t')) == 2])
    d['CG'] = 'Republic of the Congo'
    d['KR'] = 'South Korea'
    d['MA'] = 'Morocco'
    d['CO'] = 'Colombia'
    d['FR'] = 'France'
    d['AL'] = 'Albania'
    d['IR'] = 'Iran'
    d['UA'] = 'Ukraine'
    d['DE'] = 'Germany'
    d['BI'] = 'Burundi'
    d['TH'] = 'Thailand'
    return d



gender = {'M':'male','F':'female'}
group = {1: 'native children 7 - 11', 2: 'native children 12 - 16', 
    3: 'non-native children', 4: 'non-native adults', 
    5: 'native adults above 65'}
simple_group = {1: 'native children', 2: 'native children', 
    3: 'non-native children', 4: 'non-native adults', 
    5: 'native adults'}
dialect_codes = {
    "FL1": "West-Flanders",
    "FL2": "East-Flanders",
    "FL3": "Antwerp, Flemish Brabant",
    "FL4": "Limburg",
    "N1a": "South-Holland (excl. Goeree Overflakee)",
    "N1b": "North-Holland (excl. West Friesland)",
    "N1c": "West Utrecht (incl. the city of Utrecht)",
    "N2a": "Zeeland (incl. Goeree Overflakee and Zeeland Flanders)",
    "N2b": "Eastern Utrecht (excl. the city of Utrecht)",
    "N2c": "Gelders river area (incl. Arnhem and Nijmegen)",
    "N2d": "Veluwe as far as the IJssel",
    "N2e": "West Friesland",
    "N2f": "Polders",
    "N3a": "Achterkhoek",
    "N3b": "Overijssel",
    "N3c": "Drenthe",
    "N3d": "Groningen",
    "N3e": "Friesland",
    "N4a": "Noord-Brabant",
    "N4b": "Limburg",
    '1': 'West-Dutch core region',
    '2': 'Dutch Transition region',
    '3': 'Dutch Northern peripheral region',
    '4': 'Dutch Southern peripheral region',
}
comment = {'0':'no comment', '1':'Northern Dutch accent dominates', 
    'N':'Speak french at home, but are very proficient in Dutch'}
education = {'1':'primary school', '2':'secondary school',
    '3':'higher education up to 3 years', 
    '4':'higher education more than 3 years'}
