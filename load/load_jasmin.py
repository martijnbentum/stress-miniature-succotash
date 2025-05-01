from load import load_bpc
from load import load_cgn_audio
from load import load_cgn_speakers
from load import load_cgn_textgrids
from load import load_cgn_words
from load import load_cgn_phonemes
from utils import locations


def handle_cgn():
    print("Loading CGN")
    print('handling bpcs')
    load_bpc.handle_bpcs()
    print('handling audio')
    load_jasmin_audio.handle_audio_files()
    print('handling speakers')
    load_cgn_speakers.add_all_speakers()
    print('handling textgrids')
    load_cgn_textgrids.load_in_all_awd_textgrids()
    print('handling words')
    load_cgn_words.load_all_words()
    print('handling phonemes')
    load_cgn_phonemes.load_all_phonemes()
