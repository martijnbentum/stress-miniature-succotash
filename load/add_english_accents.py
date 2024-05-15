import json
from load import load_cv_speakers
from progressbar import progressbar
from text.models import Speaker

def load_speaker_ids():
    spk_ids = json.load(open('english_cv_speaker_ids.json'))
    return spk_ids

def make_speaker_dict():
    speaker_dict = {}
    d = load_cv_speakers.validated_dict('english')
    for spk_id in spk_ids:
        speaker = Speaker.objects.get(pk=spk_id)

def find_accent(speaker,d = None):
    if d is None:
        d = load_cv_speakers.validated_dict('english')
    o = []
    for line in d.values():
        if line['client_id'] == speaker.identifier:
            return line['accents']
    raise ValueError('Speaker not found')

def add_accent_to_speaker(speaker, d = None):
    if d is None:
        d = load_cv_speakers.validated_dict('english')
    accent = find_accent(speaker,d)
    speaker.info = json.dumps({'accent': accent})
    speaker.save()

def add_accent_to_speakers(d = None):
    if d is None:
        d = load_cv_speakers.validated_dict('english')
    spk_ids = json.load(open('english_cv_speaker_ids.json'))
    speakers = Speaker.objects.filter(pk__in=spk_ids)
    for speaker in progressbar(speakers):
        add_accent_to_speaker(speaker,d)

def add_accent_to_words():
    spk_ids = json.load(open('english_cv_speaker_ids.json'))
    speakers = Speaker.objects.filter(pk__in= spk_ids)
    for speaker in progressbar(speakers):
        _add_accent_to_words_speaker(speaker)

def _add_accent_to_words_speaker(speaker):
    for word in speaker.word_set.all():
        _add_accent_to_word(speaker, word)

def _add_accent_to_word(speaker, word):
        info = json.loads(word.info)
        info['accent'] = json.loads(speaker.info)['accent']
        word.info = json.dumps(info)
        word.save()

def make_accent_dict():
    d = {}
    d[''] = 'eng-US'
    d['newzealand'] = 'eng-NZ'
    d['wales'] = 'eng-GB'
    d['malaysia'] = 'eng-US'
    d['indian'] = 'eng-GB'
    d['australia'] = 'eng-AU'
    d['bermuda'] = 'eng-US'
    d['philippines'] = 'eng-US'
    d['us'] = 'eng-US'
    d['southatlandtic'] = 'eng-US'
    d['hongkong'] = 'eng-GB'
    d['african'] = 'eng-GB'
    d['singapore'] = 'eng-US'
    d['canada'] = 'eng-US'
    d['other'] = 'eng-US'
    d['ireland'] = 'eng-GB'
    d['scotland'] = 'eng-SC'
    d['england'] = 'eng-GB'
    return d
    

def make_sentence_id_accent_dict():
    _, t = load_cv_speakers.load_validated('english')
    ad = make_accent_dict()
    d = {}
    for line in t:
        if not line: continue
        if len(line) == 1: continue
        sentence_id = line[1]
        accent = line[-1]
        d[sentence_id] = ad[accent]
    return d    
        

