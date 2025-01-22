import json
from pathlib import Path 
from progressbar import progressbar
from utils import locations
from utils import overlap

def make_word_identifier(textgrid_id,speaker_id,word_index):
    return textgrid_id + '_' + speaker_id + '_' + str(word_index)

def turn_timestamps_to_dialogue_timestamps(word):
    turn_start_time = json.loads(word.audio.info)['start_time']
    start_time = word.start_time + turn_start_time
    end_time = word.end_time + turn_start_time
    return start_time, end_time

def _get_overlapping_words(word, other_words):
    word_overlap_identifiers = []
    s1, e1= turn_timestamps_to_dialogue_timestamps(word)
    for other_word in other_words:
        s2, e2 = turn_timestamps_to_dialogue_timestamps(other_word)
        if overlap.overlap(s1,e1,s2,e2, strict = True):
            word_overlap_identifiers.append(other_word.identifier)
    return word_overlap_identifiers

def _set_word_overlap(word):
    from text.models import Speaker, Audio
    audio_info = json.loads(word.audio.info)
    overlap_ids = audio_info['overlap_ids']
    other_words= []
    for overlap_id in overlap_ids:
        audio = Audio.objects.get(identifier = overlap_id)
        other_words += list(audio.word_set.all())
    word_overlap_identifiers= _get_overlapping_words(word, other_words)
    if len(word_overlap_identifiers) > 0:
        info = json.loads(word.info)
        info['word_overlap_identifiers'] = word_overlap_identifiers
        word.info = json.dumps(info)
        word.overlap = True
        word.save()
        return True
    return False

def set_words_overlap():
    from text.models import Word, Dataset
    d = Dataset.objects.get(name = 'IFADV')
    words = Word.objects.filter(dataset = d)
    overlap_count = 0
    for word in progressbar(words): 
        overlaps = _set_word_overlap(word)
        if overlaps: overlap_count += 1
    print(f'Found {overlap_count} overlapping words')
        
    

def load_all_words(start_index = 0):
    from text.models import Textgrid, Language, Dataset
    n_created = 0
    language = Language.objects.get(language__iexact='dutch')
    dataset = Dataset.objects.get(name = 'IFADV')
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
    if not Path(textgrid.filename).exists():
        print(f'File {textgrid.filename} does not exist')
        return 0
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
