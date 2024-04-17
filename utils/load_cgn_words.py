import json
from utils import locations as locations
from utils import overlap
from pathlib import Path 
from progressbar import progressbar

def make_word_identifier(textgrid_id,speaker_id,word_index):
    return textgrid_id + '_' + speaker_id + '_' + str(word_index)

def load_all_words(start_index = 0):
    from text.models import Textgrid
    n_created = 0
    for textgrid in progressbar(Textgrid.objects.all()[start_index:]):
        n = handle_textgrid(textgrid)
        n_created += n
    print(f'Created {n_created} words in total')

def handle_textgrid(textgrid):
    n_created = 0
    for speaker in textgrid.speakers.all():
        n_speaker_words = handle_speaker(speaker, textgrid)
        n_created += n_speaker_words
    print(f'Created {n_created} words for {textgrid.identifier}')
    return n_created


def handle_speaker(speaker, textgrid):
    word_tier = textgrid.load()[speaker.identifier]
    word_index = 0
    n_created = 0
    for interval_index, word_interval in enumerate(word_tier):
        created, ok = handle_word(word_interval, word_index, speaker, textgrid,
            interval_index)
        if ok: word_index += 1
        if created: n_created += 1
    print(f'Created {n_created} words for {speaker.identifier}') 
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

    
def check_overlap(word_interval, speaker, textgrid):
    tg = textgrid.load()
    other_speakers = [s for s in textgrid.speakers.all() if s != speaker]
    other_intervals = [tg[s.identifier] for s in other_speakers]
    s1,e1 = word_interval.xmin, word_interval.xmax
    for other_interval in other_intervals:
        if not hasattr(other_interval,'text'): continue
        if other_interval.text.strip('.?!') in ['',' ','_']: continue
        s2,e2 = other_interval.xmin, other_interval.xmax
        if overlap.overlap(s1,e1,s2,e2): return True
    return False
    

def handle_word(word_interval, word_index, speaker, textgrid, interval_index):
    from text.models import Word, Language
    word =  clean_text(word_interval.text)
    if not word: return False, False
    phoneme_interval=textgrid.load()[speaker.identifier+'_FON'][interval_index]
    d = {}
    d['identifier'] = make_word_identifier(textgrid.identifier, 
        speaker.identifier, word_index)
    '''
    try: Word.objects.get(identifier=d['identifier'])
    except Word.DoesNotExist: pass
    else: return False, True
    '''
    d['dataset'] = textgrid.audio.dataset
    d['speaker'] = speaker
    d['index'] = word_index
    d['word'] = word
    d['isolation'] = False
    d['overlap'] = check_overlap(word_interval, speaker, textgrid)
    d['audio'] = textgrid.audio
    d['start_time'] = word_interval.xmin
    d['end_time'] = word_interval.xmax
    d['info'] = get_word_info(word_interval,phoneme_interval, interval_index)
    d['language'] = Language.objects.get(language='Dutch')
    word, created = Word.objects.get_or_create(**d)
    return created, True
