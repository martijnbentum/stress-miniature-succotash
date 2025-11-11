from text.models import Word, Syllable, Language, Dataset, Audio
from w2v2_hidden_states import frame

def get_all_word_boundaries(language_name):
    l = Language.objects.get(language__iexact = language_name)
    audios = Audio.objects.filter(language = l)
    all_boundaries = {}
    for audio in audios:
        boundaries = get_word_boundaries(audio)
        all_boundaries[audio.filename] = boundaries
    return all_boundaries

def get_word_boundaries(audio):
    '''load all words for an audio file and return their boundaries
    '''
    words = audio.word_set.all()
    f = audio.filename
    boundaries = [(x.start_time,x.end_time, x.word, f) for x in words]
    return boundaries




