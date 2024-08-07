from audio import audio
from audio import formants as f
from audio import frequency_band
from audio import intensity
from audio import pitch
from progressbar import progressbar

def handle_all_languages():
    '''compute all acoustic measures of all phonemes in all languages'''
    from text.models import Language
    languages = Language.objects.all()
    for language in languages:
        handle_language(language.language)

def handle_language(language_name):
    '''compute all acoustic measures of all phonemes in a language'''
    from text.models import Language
    language = Language.objects.get(language__iexact = 
        language_name)
    audios = language.audio_set.all()
    print(language_name,'handling audios',audios.count())
    handle_audios(audios)

def handle_audios(audios):
    for audio_instance in progressbar(audios):
        handle_audio(audio_instance)

def handle_audio(audio_instance):
    '''compute all acoustic measures of all phonemes in an audio object'''
    formants = f.Formants(audio_instance)
    signal, sr = audio.load_audio(audio_instance)
    words = audio_instance.word_set.all()
    for word in words:
        _ = handle_word(word, signal, sr, formants)

def handle_word(word, signal, sr, formants):
    phonemes = word.phoneme_set.all()
    for phoneme in phonemes:
        f.handle_phoneme(phoneme, formants, save = False)
        frequency_band.handle_phoneme(phoneme, signal, sr, save = False)
        intensity.handle_phoneme(phoneme, signal, sr, save = False)
        pitch.handle_phoneme(phoneme, signal, sr, save = False)
        phoneme.save()

