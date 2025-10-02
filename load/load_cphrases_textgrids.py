from load import load_cphrases_audio 
import textgrids
from pathlib import Path 
from progressbar import progressbar
from utils import locations 

def load_in_all_textgrids():
    n_created = 0
    filenames = list(get_textgrid_filenames())
    for filename in progressbar(filenames):
        created = load_in_maus_textgrid(filename)
        if created: n_created += 1
    print('found',len(filenames), 'textgrids for CGN phrases')
    print('created',n_created, 'textgrids for CGN phrases')

def get_textgrid_filenames():
    fn = locations.cgn_phrases_textgrids.glob('*.TextGrid')
    return fn

def textgrid_filename_to_audio(filename):
    from text.models import Audio
    identifier = Path(filename).stem
    try:
        return Audio.objects.get(identifier=identifier)
    except Audio.DoesNotExist:
        return None

def textgrid_filename_to_speaker(filename):
    from text.models import Speaker
    identifier = Path(filename).stem
    speaker_id = identifier.split('_')[0]
    try:
        return Speaker.objects.get(identifier=speaker_id)
    except Speaker.DoesNotExist:
        return None

def audio_to_speaker(audio):
    from text.models import Speaker
    speaker_id = audio.identifier.split('_')[0]
    try:
        return Speaker.objects.get(identifier=speaker_id)
    except Speaker.DoesNotExist:
        return None

def load_in_maus_textgrid(filename):
    from text.models import Textgrid, Dataset
    dataset = Dataset.objects.get(name = 'cgn-phrases')
    audio = textgrid_filename_to_audio(filename)
    speaker = audio_to_speaker(audio)
    d ={}
    d['identifier'] = Path(filename).stem
    d['audio'] = audio
    d['filename'] = filename
    d['phoneme_set_name'] = 'maus'
    d['dataset'] = dataset
    textgrid, created = Textgrid.objects.get_or_create(**d)
    if created:
        textgrid.speakers.add(speaker)
    return created


