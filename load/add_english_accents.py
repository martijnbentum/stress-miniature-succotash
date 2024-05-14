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

    
        

