from utils import align_syllables
from utils import celex
import json
from load import load_cv_audio as lca
from progressbar import progressbar

def handle_language(language_name):
    language_name = language_name.lower()
    if language_name in  ['dutch', 'english', 'german']:
        handle_celex_languages(language_name)
    if language_name == 'hungarian':
        handle_hungarian()
    if language_name == 'polish':
        handle_polish()
    if language_name == 'french':
        handle_french()
    if language_name == 'spanish':
        handle_spanish()


def load_language_words(language_name):
    from text.models import Word
    dataset = lca.load_dataset('COMMON VOICE')
    language = lca.load_language(language_name)
    words = Word.objects.filter(language=language,
        dataset=dataset)
    return words

def handle_hungarian(word_start_index = 0):
    '''In Hungarian, the stress is mostly on the first syllable.'''
    words = load_language_words('hungarian')
    print('n hungarian words:', words.count())
    exclude_words = ['a', 'az', 'egy', 'is']
    print('excluding no stress words:', exclude_words, 
        'based on  Carol Rounds 2009:8')
    words = words.exclude(word__in=exclude_words)
    print('n hungarian words after exclusion:', words.count())
    stress_syllables = []
    no_stress_syllables = []
    print('starting from word:', word_start_index)
    for word in progressbar(words[word_start_index:]):
        syllables = word.syllables
        if not syllables: continue
        stress_syllable = syllables[0]
        handle_syllable(stress_syllable, True)
        stress_syllables.append(stress_syllable)
        if len(word.syllables) > 1:
            for syllable in syllables[1:]:
                handle_syllable(syllable, False)
                no_stress_syllables.append(syllable)
    print('n stress syllables:', len(stress_syllables))
    print('n no stress syllables:', len(no_stress_syllables))
    return stress_syllables, no_stress_syllables, words

def _handle_polish_exceptions(word, syllables):
    if len(syllables) < 3: return False
    exception = False
    if word.word == 'fizyka':
        stress_syllable = syllables[0]
        handle_syllable(stress_syllable, True)
        exception = True
    elif word.word == 'uniwersytet':
        stress_syllable = syllables[2]
        handle_syllable(stress_syllable, True)
        exception = True
    elif word.word.endswith('by') or word.word.endswith('bym'):
        if len(syllables) < 4: return False
        stress_syllable = syllables[0]
        exception = True
    elif word.word.endswith('bysmy'):
        if len(syllables) < 5: return False
        stress_syllable = syllables[2]
        exception = True
    if not exception: return False
    for syllable in syllables:
        if syllable == stress_syllable: continue
        handle_syllable(syllable, False)
    return True

def handle_polish(start_index = 0):
    '''In Polish, the stress is mostly on the penultimate syllable.'''
    words = load_language_words('polish')
    exceptions, stress_syllables, no_stress_syllables = [], [], []
    for word in progressbar(words[start_index:]):
        syllables = word.syllables
        if not syllables: continue
        exception = _handle_polish_exceptions(word, syllables)
        if exception:
            exceptions.append(word)
            continue
        if len(syllables) < 3:
            stress_syllable = syllables[0]
        else:
            stress_syllable = syllables[-2]
        for syllable in syllables:
            if syllable == stress_syllable:
                handle_syllable(syllable, True)
                stress_syllables.append(syllable)
            else:
                handle_syllable(syllable, False)
                no_stress_syllables.append(syllable)
    return stress_syllables, no_stress_syllables, words, exceptions

def handle_french():
    words = load_language_words('french')
    for word in progressbar(words):
        syllables = word.syllables
        if not syllables: continue
        stress_syllable = syllables[-1]
        if len(stress_syllable.vowel) == 0: vowel = None
        else: vowel = stress_syllable.vowel[0]
        if vowel == 'ə': stress_syllable == None
        for syllable in syllables:
            if syllable == stress_syllable:
                handle_syllable(syllable, True)
            else:
                handle_syllable(syllable, False)

def handle_spanish():
    words = load_language_words('spanish')
    for word in progressbar(words):
        syllables = word.syllables
        if not syllables: continue
        if len(syllables) == 1:
            stress_syllable = syllables[0]
        elif word.word.endswith('n') or word.word.endswith('s'):
            stress_syllable = syllables[-2]
        elif word.phonemes and 'consonant' in word.phonemes[-1].bpcs_str: 
            stress_syllable = syllables[-1]
        for syllable in syllables:
            if syllable == stress_syllable:
                handle_syllable(syllable, True)
            else:
                handle_syllable(syllable, False)

def handle_celex_languages(language_name):
    if language_name not in  ['dutch', 'english', 'german']:
        raise ValueError('Language not a celex language',
            language_name)
    c = celex.Celex(language_name.lower())
    words = load_language_words(language_name)
    for word in progressbar(words):
        handle_word_celex(word, c)

def handle_word_celex(word, celex):
    align = align_syllables.Aligner(word, celex)
    syllables = align.syllables
    for syllable in syllables:
        handle_syllable(syllable, False)
    stressed_syllable = align.stressed_syllable
    handle_syllable(stressed_syllable, True)
    handle_word_info_celex(word, align, stressed_syllable)

def handle_word_info_celex(word, align, stressed_syllable):
    info = word.info_dict
    info['based_on'] = align.based_on
    if align.celex_word:
        info['celex_word'] = align.celex_word.line
    else:info['celex_word'] = None
    info['stressed_syllable'] = stressed_syllable != None
    word.info = json.dumps(info)
    word.save()

def handle_syllable(syllable, stress):
    if not syllable: return
    syllable.stress = stress
    syllable.save()
    for phoneme in syllable.phoneme_set.all():
        phoneme.stress = stress
        phoneme.save()
         

        
