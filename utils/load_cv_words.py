import json
from utils import locations as locations
from pathlib import Path 
from progressbar import progressbar

def make_word_identifier(textgrid_id,speaker_id,word_index):
    return textgrid_id + '_' + speaker_id + '_' + str(word_index)


def load_all_words_language(language_name, start_index = 0):
    from text.models import Textgrid, Language, Dataset
    n_created = 0
    language = Language.objects.get(language__iexact=language_name)
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    textgrids = Textgrid.objects.filter(audio__language = language,
        audio__dataset = dataset)
    for textgrid in progressbar(textgrids[start_index:]):
        n = handle_textgrid(textgrid, language, dataset)
        n_created += n
    print(f'Created {n_created} words in total')

def handle_textgrid(textgrid,language, dataset):
    n_created = 0
    for speaker in textgrid.speakers.all():
        n_speaker_words = handle_speaker(speaker, textgrid, language, dataset)
        n_created += n_speaker_words
    return n_created

def handle_speaker(speaker, textgrid, language, dataset):
    word_tier = textgrid.load()['ORT-MAU']
    word_index = 0
    n_created = 0
    for interval_index, word_interval in enumerate(word_tier):
        created, ok = handle_word(word_interval, word_index, speaker, textgrid,
            interval_index, language, dataset)
        if ok: word_index += 1
        if created: n_created += 1
    return n_created

def clean_text(text):
    if '!' in text: return None
    t = text.strip(' .?')
    if ' ' in t: return None #exclude multiple words
    t = t.split('*')[0]
    if t.lower() in ['',' ','_','ggg','xxx']: return None
    return t

def get_word_info(word_interval, phoneme_interval, interval_index):
    info = {}
    info['eos'] = '.' in word_interval.text or '?' in word_interval.text
    info['special_word'] = '*' in word_interval.text 
    info['word_phoneme'] = phoneme_interval.text
    info['interval_index'] = interval_index
    return json.dumps(info)

def handle_word(word_interval, word_index, speaker, textgrid, interval_index,
    language, dataset):
    from text.models import Word
    word =  clean_text(word_interval.text)
    if not word: return False, False
    phoneme_interval=textgrid.load()['KAN-MAU'][interval_index]
    audio = textgrid.audio
    d = {}
    d['identifier'] = make_word_identifier(textgrid.identifier, 
        speaker.identifier, word_index)
    d['dataset'] = dataset
    d['speaker'] = speaker
    d['index'] = word_index
    d['word'] = word
    d['isolation'] = False
    d['overlap'] = False
    d['audio'] = audio
    d['start_time'] = word_interval.xmin
    d['end_time'] = word_interval.xmax
    d['info'] = get_word_info(word_interval,phoneme_interval, interval_index)
    d['language'] = language
    word, created = Word.objects.get_or_create(**d)
    return created, True
