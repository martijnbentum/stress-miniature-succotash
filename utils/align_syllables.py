from utils import needleman_wunch as nw
from utils import celex
import json

def word_to_celex_word(word, celex_database = None):
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    if not celex_word:
        celex_word = celex_database.get_word(word.word.lower())
    return celex_word

def get_stressed_syllable(word, celex_database = None):
    syllables = word.syllable_set.all()
    if len(syllables) == 1: 
        print('only one syllable, it has primary stress', word.word)
        return syllables[0]
    celex_word = word_to_celex_word(word, celex_database)
    if not celex_word: 
        print('celex word not found', word.word)
        return None
    if not celex_word.syllables:
        print('no syllables in celex word', word.word)
        return None
    stressed_syllable_index = celex_word.stress_list.index('primary')
    stressed_syllable = syllables[stressed_syllable_index]
    print(celex_word,'\n',word,'\n',
        celex_word.syllables[stressed_syllable_index], '\n',
        stressed_syllable, stressed_syllable_index)
    return stressed_syllable



def align_celex_maus_phonemes(celex_word, maus_word, word_phonemes= None):
    if not word_phonemes: word_phonemes = maus_word.phoneme_set.all()
    celex_ipa = [x[0] for x in celex_word.ipa.split(' ')]
    word_ipa = [x[0] for x in maus_word.ipa.split(' ')]
    celex_ipa, word_ipa = nw.nw(celex_ipa,word_ipa).split('\n')
    celex_phonemes = ipa_to_instances(celex_ipa, celex_word.phonemes)
    word_phonemes = ipa_to_instances(word_ipa, word_phonemes)
    output = []
    for word_phoneme,celex_phoneme in zip(word_phonemes,celex_phonemes):
        if not word_phoneme: continue
        word_phoneme.celex_phoneme = celex_phoneme
        output.append(word_phoneme)
    return celex_ipa, word_ipa, celex_phonemes, word_phonemes, output

def ipa_to_instances(ipa, word_phonemes):
    output = []
    phoneme_index = 0
    for phoneme in ipa:
        if phoneme == '-': 
            output.append(None)
            continue
        output.append(word_phonemes[phoneme_index])
        phoneme_index += 1
    return output

def align_with_celex_word(word, celex_database = None):
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    add_celex_to_word(word, celex_word)
    celex_syllables = celex_word.syllables
    word_syllables = word.syllable_set.all()

def add_celex_to_word(word, celex_word):
    info = json.loads(word.info)
    info['celex_word'] = celex_word.line
    word.info = json.dumps(info)
    word.save()
