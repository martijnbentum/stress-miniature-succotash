from utils import locations as locations
import textgrids
from pathlib import Path 
from progressbar import progressbar

def get_awd_textgrid_filename(filename):
    '''
    filename can be cgn_id e.g. fn00088
    '''
    d = locations.cgn_awd
    name = Path(filename).stem
    fn = d.glob( '*.awd' )
    for f in fn:
        if name == f.stem:
            return f

def load_in_awd_textgrid(audio):
    from text.models import Textgrid, Speaker
    filename = get_awd_textgrid_filename(audio.filename)
    tg = textgrids.TextGrid(filename)
    speaker_ids = [k for k in tg.keys() if '_' not in k]
    speakers = Speaker.objects.filter(identifier__in=speaker_ids)
    if not filename: return None
    d ={}
    d['identifier'] = Path(filename).stem
    d['audio'] = audio
    d['filename'] = filename
    d['phoneme_set_name'] = 'cgn'
    textgrid, created = Textgrid.objects.get_or_create(**d)
    linked_speakers = textgrid.speakers.all()
    for speaker in speakers:
        if speaker not in linked_speakers:
            textgrid.speakers.add(speaker)
    return textgrid, created

def load_in_all_awd_textgrids():
    from text.models import Audio
    audios = Audio.objects.all()
    print('audios',audios.count())
    no_file = []
    ncreated = 0
    for audio in progressbar(audios):
        _, created = load_in_awd_textgrid(audio)
        if created: ncreated += 1
        if created == None: no_file.append(audio.filename)
    print('ncreated',ncreated)
    print('no_file',' '.join(no_file))

def load_awd_textgrid(filename):
    f = get_awd_textgrid_filename(filename)
    return textgrids.TextGrid(f)


def intervals_to_dict(intervals):
    d={}
    for i, iv in enumerate(intervals):
        d[i] = '\t'.join(map(str,[iv.text,iv.xmin,iv.xmax]))
    return d
