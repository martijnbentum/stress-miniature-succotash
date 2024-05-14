from utils import locations
from load import add_english_accents

maus_exclude_phonemes = '#,>,<,<usb>,<nib>,<p:>,<p>'.split(',') 

def load_file(language, accent_code=None):
    language = language.lower()
    if accent_code: ac = accent_code.split('-')[-1].lower()
    root_folder = locations.get_language_cv_root_folder(language)
    filename = root_folder / f'maus_{language}_{ac}_phoneme_map.txt'  
    with open(filename, 'r') as f:
        t = f.read().split('\n')
    t = [x for x in t if not x.startswith('%') and x]
    header, data = t[0].split('\t'), t[1:]
    output = []
    for line in data:
        line = line.split('\t')
        output.append(dict(zip(header, line)))
    return output

class Maus:
    def __init__(self, language, accent=None): 
        ad = add_english_accents.make_accent_dict()
        if language.lower() == 'english': 
            if accent == None: 
                raise ValueError('accent must be provided for English')
            if accent not in ad.keys():
                raise ValueError(f'accent {accent} not recognized')
        accent_code = ad[accent] if accent != None else None
        self.accent = accent
        self.accent_code = accent_code
        self.language = language
        self.raw = load_file(language, accent_code)

    def __repr__(self):
        m = f'Maus phoneme mapper for: {self.language} '
        if self.accent_code: m += f'{self.accent} {self.accent_code}'
        return m

    def maus_to_ipa(self):
        d = {}
        for line in self.raw:
            if line['MAUS'] in maus_exclude_phonemes: 
                continue
            d[line['MAUS']] = line['IPA']
        return d

    def sampa_to_ipa(self):
        d = {}
        for line in self.raw:
            if line['MAUS'] in maus_exclude_phonemes: 
                continue
            d[line['SAMPA']] = line['IPA']
        return d

    def ipa_to_lines(self):
        d = {}
        for line in self.raw:
            if line['MAUS'] in maus_exclude_phonemes: 
                continue
            d[line['IPA']] = line
        return d

    def ipa_to_maus(self):
        d = {}
        for line in self.raw:
            if line['MAUS'] in maus_exclude_phonemes: 
                continue
            d[line['IPA']] = line['MAUS']
        return d
