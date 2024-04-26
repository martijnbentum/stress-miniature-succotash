import textgrids
from pathlib import Path 
from progressbar import progressbar
from utils import locations 

def get_textgrid_filename(audio_filename):
    name = Path(audio_filename).stem
    speaker_dir = name[:4]
    #filename=locations.coolest_textgrids / f'{speaker_dir}/{name}_cor.TextGrid'
    filename = locations.coolest_textgrids / f'{name}.TextGrid'
    if not filename.exists(): raise FileNotFoundError(filename)
    return filename

def load_in_textgrid(audio):
    from text.models import Textgrid, Speaker
    filename = get_textgrid_filename(audio.filename)
    tg = textgrids.TextGrid(filename)
    speaker_id = (filename).stem[:4]
    speaker = Speaker.objects.get(identifier=speaker_id)
    d ={}
    d['identifier'] = 'coolest_' + Path(filename).stem
    d['audio'] = audio
    d['filename'] = filename
    d['phoneme_set_name'] = 'maus'
    textgrid, created = Textgrid.objects.get_or_create(**d)
    textgrid.speakers.add(speaker)
    return textgrid, created

def load_in_all_textgrids():
    from text.models import Audio
    audios = Audio.objects.filter(dataset__name='coolest')
    print('audios',audios.count())
    no_file = []
    ncreated = 0
    for audio in progressbar(audios):
        _, created = load_in_textgrid(audio)
        if created: ncreated += 1
        if created == None: no_file.append(audio.filename)
    print('ncreated',ncreated)
    print('no_file',' '.join(no_file))


