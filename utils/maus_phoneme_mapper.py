from utils import locations

maus_exclude_phonemes = '#,>,<,<usb>,<nib>,<p:>,<p>'.split(',') 

def load_file(language):
    language = language.lower()
    root_folder = locations.get_language_cv_root_folder(language)
    filename = root_folder / f'maus_{language}_phoneme_map.txt'  
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
    def __init__(self, language):
        self.language = language
        self.raw = load_file(language)

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
