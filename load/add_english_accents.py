import json
from load import load_cv_speakers
from progressbar import progressbar
from text.models import Speaker


def make_speaker_dict():
    spk_ids = json.load(open('english_cv_speaker_ids.json'))
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
    t = load_validated()
    d = {}
    for line in t[1:]:
        if line == '': continue
        line = line.split('\t')
        sentence_id = line[1]
        accent = line[-1]
        if accent == '': accent = 'eng-US'
        if accent == 'newzealand': accent = 'eng-NZ'
        if accent == 'wales': accent = 'eng-GB'
        if accent == 'malaysia': accent = 'eng-US'
        if accent == 'indian': accent = 'eng-GB'
        if accent == 'australia': accent = 'eng-AU'
        if accent == 'bermuda': accent = 'eng-US'
        if accent == 'philippines': accent = 'eng-US'
        if accent == 'us': accent = 'eng-US'
        if accent == 'southatlandtic': accent = 'eng-US'
        if accent == 'hongkong': accent = 'eng-GB'
        if accent == 'african': accent = 'eng-GB'
        if accent == 'singapore': accent = 'eng-US'
        if accent == 'canada': accent = 'eng-US'
        if accent == 'other': accent = 'eng-US'
        if accent == 'ireland': accent = 'eng-GB'
        if accent == 'scotland': accent = 'eng-SC'
        if accent == 'england': accent = 'eng-GB'
        d[sentence_id] =accent
    return d    
        

