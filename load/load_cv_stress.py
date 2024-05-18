from utils import align_syllables
from utils import celex
import json
from load import load_cv_audio as lca
from progressbar import progressbar


def handle_language(language_name):
    from text.models import Word
    if not language_name == 'dutch':
        raise ValueError('Language not supported',
            language_name)
    c = celex.Celex('dutch')
    dataset = lca.load_dataset('COMMON VOICE')
    language = lca.load_language(language_name)
    words = Word.objects.filter(language=language,
        dataset=dataset)
    for word in progressbar(words):
        handle_word(word, c)

def handle_word(word, celex):
    align = align_syllables.Aligner(word, celex)
    syllables = align.syllables
    for syllable in syllables:
        handle_syllable(syllable, False)
    stressed_syllable = align.stressed_syllable
    handle_syllable(stressed_syllable, True)
    handle_word_info(word, align, stressed_syllable)

def handle_word_info(word, align, stressed_syllable):
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
         

        
