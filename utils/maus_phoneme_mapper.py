from utils import locations

def load_file(language):
    pass

class Maus:
    def __init__(self, language):
        self.language = language
        self.raw = load_file(language)
        self.phoneme_mapper = PhonemeMapper()
