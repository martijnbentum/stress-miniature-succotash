from text.models import Word

def _check_next_word(word, next_word, delta_between_words = 0.5):
    if word.audio != next_word.audio:
        raise ValueError(f'Words {word} and {next_word} are not in the same audio')
    if word.index + 1 != next_word.index:
        raise ValueError(f'Words {word} and {next_word} are not consecutive')
    if word.end_time > next_word.start_time:
        raise ValueError(f'Words {word} and {next_word} overlap in time')
    delta = next_word.end_time - word.end_time
    if delta > delta_between_words:
        m = f'Too much time between {word} and {next_word}, {delta:.2f}'
        raise ValueError(m)

def select_words_and_next(word = 'zij', onset_ipa_next_word = None, 
    onset_phone_type_next_word = None, delta_between_words = 0.5, 
    ipas_first_word = None, language_name = None, verbose = False,):
    if onset_phone_type_next_word not in ['vowel', 'consonant', None]:
        m = 'onset_next_word_phone_type must be vowel, consonant or None'
        raise ValueError(m)
    if language_name: words = Word.objects.filter(word__iexact = word, 
        language__language__iexact = language_name)
    else:words = Word.objects.filter(word__iexact = word)
    n_words = len(words)
    if ipas_first_word:
        if type(ipas_first_word) == list:
            words = words.filter(ipa__in = ipas_first_word)
            n = len(words)
        else:
            words = words.filter(ipa = ipas_first_word)
            n = len(words)
    m = f'found {n_words} words matching {word}'
    if ipas_first_word: m += f', {n} matching the ipa criteria'
    print(m)
    next_words = []
    for word in words:
        try:next_word = word.audio.word_set.all()[word.index + 1]
        except IndexError:
            if verbose: print(f'Word {word} is the last word in the audio')
            continue
        try: _check_next_word(word, next_word)
        except ValueError as ve:
            if verbose: print(ve)
            continue
        next_word_onset = next_word.phonemes[0]
        if onset_ipa_next_word:
            if next_word_onset.ipa != onset_ipa_next_word:
                continue
        if onset_phone_type_next_word:
            phone_type = next_word_onset.bpcs_str.split(',')
            if onset_phone_type_next_word not in phone_type:
                continue
        next_words.append([word,next_word])
    return next_words

def make_zij_zijn_dataset(onset_ipa_next_word = 'n', 
    delta_between_words = 0.5, verbose = False, language_name = 'Dutch'):
    zij_ipas = ['s ɛi', 'z ɛi']
    zij_and_next = select_words_and_next(word = 'zij',
        onset_ipa_next_word = onset_ipa_next_word,
        delta_between_words = delta_between_words,
        ipas_first_word = zij_ipas, language_name = language_name,
        verbose = verbose,)
    zijn_ipas = ['z ɛi n', 's ɛi n']
    zijn_and_next = select_words_and_next(word = 'zijn',
        onset_phone_type_next_word = 'vowel',
        delta_between_words = delta_between_words,
        ipas_first_word= zijn_ipas, language_name = language_name,
        verbose = verbose,)
    return {'zij':zij_and_next, 'zijn':zijn_and_next}




        
