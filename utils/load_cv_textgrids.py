from utils import locations 
from utils import load_cv_audio 
from utils import load_cv_speakers 
import textgrids
from pathlib import Path 
from progressbar import progressbar

def get_maus_textgrid_filename(filename, cv_root_folder ):
    '''
    filename should be a cv audio filename common_voice_nl_17704684.mp3
    '''
    filename = Path(filename).stem + '.TextGrid'
    textgrid_folder = locations.get_cv_path(cv_root_folder, 'textgrids')
    return textgrid_folder / filename

def load_speaker(audio, validated_dict):
    from text.models import Speaker
    audio_filename = Path(audio.filename).name
    if not audio_filename in validated_dict.keys(): return False
    line = validated_dict[audio_filename]
    speaker = Speaker.objects.get(identifier=line['client_id'])
    return speaker
    
def load_in_maus_textgrid(audio,cv_root_folder,validated_dict):
    from text.models import Textgrid
    filename = get_maus_textgrid_filename(audio.filename, cv_root_folder)
    speaker = load_speaker(audio, validated_dict)
    d ={}
    d['identifier'] = Path(filename).stem
    d['audio'] = audio
    d['filename'] = filename
    d['phoneme_set_name'] = 'maus'
    textgrid, created = Textgrid.objects.get_or_create(**d)
    if created:
        textgrid.speakers.add(speaker)
    return created

def handle_language(language_name):
    from text.models import Audio
    cv_root_folder = load_cv_audio.get_language_root_folder(language_name)
    validated_dict = load_cv_speakers.validated_dict(language_name)
    language = load_cv_audio.load_language(language_name)
    dataset = load_cv_audio.load_dataset('COMMON VOICE')
    audios = Audio.objects.filter(language=language, dataset=dataset)
    n_created = 0
    for audio in progressbar(audios):
        created = load_in_maus_textgrid(audio, cv_root_folder, validated_dict)
        if created: n_created += 1
    print('created',n_created, 'textgrids for',language_name)



def handle_all_languages():
    ncreated = 0
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        handle_language(language)
        _, created = load_in_awd_textgrid(audio)
        if created: ncreated += 1
        if created == None: no_file.append(audio.filename)
    print('ncreated',ncreated)
    print('no_file',' '.join(no_file))



