from utils import load_cv_audio
from utils import load_cv_speakers
from utils import load_cv_textgrids
from utils import load_cv_words
from utils import load_cv_phonemes
from utils import load_cv_syllables


def handle_language(language_name):
    print("Loading CV for language: " + language_name)
    print('handling audio')
    load_cv_audio.handle_language(language_name)
    print('handling speakers')
    load_cv_speakers.handle_language(language_name)
    print('handling textgrids')
    load_cv_textgrids.handle_language(language_name)
    print('handling words')
    load_cv_words.load_all_words_language(language_name)
    print('handling phonemes')
    load_cv_phonemes.handle_language(language_name)
    print('handling syllables')
    load_cv_syllables.handle_language(language_name)
        

def handle_languages(languages):
    for language in languages:
        handle_language(language)

def handle_all_languages():
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        handle_language(language)
