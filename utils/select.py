def select_phonemes(language_name, stress, dataset = 'COMMON VOICE',
    minimum_n_syllables = 2):
    '''
    Select phonemes based on language, stress, dataset and number of syllables.
    '''
    from text.models import Phoneme 
    language = select_language(language_name)
    phonemes = Phoneme.objects.filter(language=language)
    if stress is not None:
        phonemes = phonemes.filter(stress=stress)
    if minimum_n_syllables is not None:
        n = minimum_n_syllables - 1
        phonemes = phonemes.filter(word__n_syllables__gt = n)
    return phonemes


def select_words(language_name, dataset = 'COMMON VOICE', 
    minimum_n_syllables = 2):
    '''
    Select words based on language, dataset and number of syllables.
    '''
    from text.models import Word
    language = select_language(language_name)
    words = words.objects.filter(language=language)
    if minimum_n_syllables is not None:
        words = Word.objects.filter(n_syllables__gt = minimum_n_syllables - 1)
    return words

def select_language(language_name):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language
