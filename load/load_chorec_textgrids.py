import textgrids
from pathlib import Path 
from progressbar import progressbar
from utils import locations 

def get_awd_textgrid_filename(filename):
    p = Path(filename)
    f = str(p)
    f = f.replace('.wav', '_a01.TextGrid')
    p = Path(f)
    if p.exists():
        return f
    raise FileNotFoundError(f'{f} does not exist. Audio file {filename}') 

def convert_to_utf8(filename, encoding = 'iso-8859-1', goal_dir = '../awd/'):
    f = Path(filename)
    with open(str(f), 'r', encoding=encoding) as infile:
        data = infile.read()
    d = Path(goal_dir)
    d.mkdir(parents=True, exist_ok=True)
    of = d / f.name
    with open(str(of), 'w', encoding='utf-8') as outfile:
        outfile.write(data)
    return str(of)

    
def get_speaker(filename):
    from text.models import Speaker
    p = Path(filename)
    sid = p.stem.split('_')[0]
    speaker = Speaker.objects.get(identifier=sid)
    return speaker

def load_in_awd_textgrid(audio):
    from text.models import Textgrid, Dataset
    filename = get_awd_textgrid_filename(audio.filename)
    filename = convert_to_utf8(filename)
    chorec = Dataset.objects.get(name='CHOREC')
    tg = textgrids.TextGrid(filename)
    speaker = get_speaker(audio.filename)
    d ={}
    d['identifier'] = Path(filename).stem
    d['audio'] = audio
    d['filename'] = filename
    d['phoneme_set_name'] = 'cgn'
    d['dataset'] = chorec
    textgrid, created = Textgrid.objects.get_or_create(**d)
    linked_speakers = textgrid.speakers.all()
    if speaker not in linked_speakers:
        textgrid.speakers.add(speaker)
    return textgrid, created

def load_in_all_awd_textgrids():
    from text.models import Audio
    audios = Audio.objects.filter(dataset__name='CHOREC')
    print('audios',audios.count())
    no_file = []
    ncreated = 0
    for audio in progressbar(audios):
        try:_, created = load_in_awd_textgrid(audio)
        except FileNotFoundError:
            if 'PAPIER' in audio.filename: continue
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
