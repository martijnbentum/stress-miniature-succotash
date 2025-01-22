import json
import textgrids
from load.load_ifadv_audio import load_wav_filename_to_speaker_id_dict
from pathlib import Path 
from progressbar import progressbar
from utils import locations 


def get_maus_textgrid_filename(filename):
    '''
    filename should be a ifadv audio filename 
    '''
    filename = Path(filename).stem + '.TextGrid'
    return locations.ifadv_textgrids / filename

def load_speaker(audio, speaker_dict = None):
    from text.models import Speaker
    if not speaker_dict:
        speaker_dict = load_wav_filename_to_speaker_id_dict()
    audio_filename = audio.filename
    if not audio_filename in speaker_dict.keys(): return False
    speaker_id= speaker_dict[audio_filename]
    speaker = Speaker.objects.get(identifier=speaker_id)
    return speaker
    
def load_in_maus_textgrid(audio, speaker_dict = None):
    from text.models import Textgrid, Dataset
    if not speaker_dict:
        speaker_dict = load_wav_filename_to_speaker_id_dict()
    filename = get_maus_textgrid_filename(audio.filename)
    speaker = load_speaker(audio)
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
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

def make_all_textgrids():
    from text.models import Audio
    language = Language.objects.get(language__iexact='dutch')
    dataset = Dataset.objects.get(name = 'IFADV')
    audios = Audio.objects.filter(language=language, dataset=dataset)
    speaker_dict = load_wav_filename_to_speaker_id_dict()
    n_created = 0
    for audio in progressbar(audios):
        created = load_in_maus_textgrid(audio, speaker_dict)
        if created: n_created += 1
    print('created',n_created, 'textgrids for IFADV')






