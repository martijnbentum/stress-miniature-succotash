from load import load_mls_phonemes
from utils import maus_phoneme_mapper
from progressbar import progressbar


def handle_language(language_name):
    from text.models import Language, Dataset
    language = Language.objects.get(language__iexact=language_name)
    dataset = Dataset.objects.get(name = 'MLS')
    handle_words(language, dataset)

def handle_words(language, dataset):
    from text.models import Word
    words = Word.objects.filter(language=language, dataset=dataset)
    n_created = 0
    for word in progressbar(words):
        n_created += handle_word(word, language, dataset)
    print('Created', n_created, 'syllables for', language.language)

def save_n_syllables(word):
    word.n_syllables = word.syllable_set.all().count()
    word.n_phonemes = word.phoneme_set.all().count()
    word.save()

def handle_word(word, language, dataset, count = 0):
    speaker = word.speaker
    audio = word.audio
    textgrid = audio.textgrid_set.get(phoneme_set_name='maus')
    syllable_intervals = word_to_syllable_intervals(word,textgrid)
    n_created = 0
    phonemes = word.phoneme_set.all()
    for syllable_index, syllable_interval in enumerate(syllable_intervals):
        syllable,created = handle_syllable(syllable_interval, syllable_index, 
            word, audio, speaker, language, phonemes, dataset, count = count)
        if created: n_created += 1
        if not syllable and count == 0: 
            return handle_word(word, language, dataset, 1)
        elif count > 1: 
            print(word,language,count, syllable_interval, '>>syllable error<<')
            continue
    save_n_syllables(word)
    return n_created

def handle_syllable(syllable_interval, syllable_index, word, audio, speaker,
    language, phonemes, dataset, count = 0):
    from text.models import Syllable, Dataset
    syllable_phonemes = select_syllable_phonemes(syllable_interval, phonemes,
        word, language, dataset, count = count)
    if not syllable_phonemes: return False, False
    d = {}
    d['identifier'] = make_syllable_identifier(word, syllable_index)
    d['phoneme_str'] = syllable_interval.text
    d['ipa'] = ' '.join([p.ipa for p in syllable_phonemes])
    d['word'] = word
    d['index'] = syllable_index
    d['start_time'] = syllable_interval.xmin
    d['end_time'] = syllable_interval.xmax
    d['audio'] = audio
    d['speaker'] = speaker
    d['language'] = language
    d['dataset'] = dataset
    syllable, created = Syllable.objects.get_or_create(**d)
    handle_phonemes(syllable, syllable_phonemes)
    return syllable, created

def handle_phonemes(syllable, phonemes):
    for index,phoneme in enumerate(phonemes):
        phoneme.syllable = syllable
        phoneme.syllable_index = index
        phoneme.save()

def make_syllable_identifier(word, syllable_index):
    return word.identifier + '_' + str(syllable_index)

def _check_phonemes_merged(phonemes, syllable_interval):
    '''phonemes can be merged in the syllable tier'''
    text = syllable_interval.text.replace(' ','')
    itm = maus_phoneme_mapper.Maus('german').ipa_to_maus()
    maus = ''.join([itm[p.ipa] for p in phonemes])
    if maus == text:
        print('phonemes merged for',text, maus)
        return True
    else:
        print('phonemes not merged for',text, maus)
        return False
        
def select_syllable_phonemes(syllable_interval, phonemes, word, language,
    dataset, count = 0):
    '''select the phonemes that belong to the syllable'''
    syllable_phonemes = []
    lname = language.language.lower()
    for phoneme in phonemes:
        if contains(phoneme.start_time, phoneme.end_time, 
            syllable_interval.xmin, syllable_interval.xmax):
            syllable_phonemes.append(phoneme)
    if len(syllable_phonemes) != len(syllable_interval.text.split(' ')):
        if '?' in syllable_interval.text and count == 0:
            print('correcting phonemes for',syllable_interval.text,
                'word:',word, 'language:',language,'syl phon',syllable_phonemes,
                count)
            word.phoneme_set.all().delete()
            word.syllable_set.all().delete()
            ln = language.language
            maus_to_ipa = maus_phoneme_mapper.Maus(ln).maus_to_ipa()
            load_mls_phonemes.handle_word(word, language, maus_to_ipa, dataset)
            return False
        elif lname == 'german' and _check_phonemes_merged(syllable_phonemes, 
            syllable_interval):
            pass
        else:
            with open('../syllable_mismatched_phonemes.txt','r') as f:
                t = f.read().split('\n')
            ipa = ' '.join([p.ipa for p in syllable_phonemes])
            text = syllable_interval.text
            identifier = word.identifier
            language = language.language
            output = '\t'.join([identifier, text, ipa, language])
            print(word,language,count, syllable_interval, '>>SYLLABLE ERROR<<')
            if output in t: return False
            with open('../syllable_mismatched_phonemes.txt','a') as f:
                f.write(output + '\n')
            word.syllable_set.all().delete()
            return False
    return syllable_phonemes

def contains(smaller_start, smaller_end, larger_start, larger_end):
    return (smaller_start >= larger_start) and (smaller_end <= larger_end)

def word_to_syllable_intervals(word,textgrid):
    all_syllable_intervals = textgrid.load()['MAS']
    output = []
    exclude = ['',' ','sp','[]'] + maus_phoneme_mapper.maus_exclude_phonemes
    for syllable_interval in all_syllable_intervals:
        if syllable_interval.text in exclude: continue
        if '!' in syllable_interval.text: continue
        start, end = syllable_interval.xmin, syllable_interval.xmax
        if start >= word.start_time and end <= word.end_time:
            output.append(syllable_interval)
    return output

