from load import load_bpc
from load import load_mls_audio
from load import load_mls_speakers
from load import load_mls_textgrids
from load import load_mls_words
from load import load_mls_phonemes
# from load import load_mls_syllables
# from load import load_mls_stress
from load import load_languages
from load import load_datasets
from utils import locations


def handle_language(language_name):
    print("Loading CV for language: " + language_name)
    print('handling bpcs')
    load_bpc.handle_bpcs()
    print('handling audio')
    load_mls_audio.handle_language(language_name)
    print('handling speakers')
    load_mls_speakers.handle_language(language_name)
    print('handling textgrids')
    load_mls_textgrids.handle_language(language_name)
    print('handling words')
    load_mls_words.load_all_words_language(language_name)
    print('handling phonemes')
    load_mls_phonemes.handle_language(language_name)
    '''
    print('handling syllables')
    load_mls_syllables.handle_language(language_name)
    print('handling stress')
    load_mls_stress.handle_language(language_name)
    '''
