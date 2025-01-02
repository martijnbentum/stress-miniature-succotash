from load import load_mls_audio 
from load import load_mls_speakers 
import textgrids
from pathlib import Path 
from progressbar import progressbar
from utils import locations 

def get_maus_textgrid_filename(filename, mls_root_folder ):
    '''
    filename should be a mls audio filename .wav
    '''
    split = Path(filename).parent.stem
    filename = Path(filename).stem + '.TextGrid'
    textgrid_folder = locations.get_mls_path(mls_root_folder, 'textgrid')
    textgrid_filename = textgrid_folder / split / filename
    return textgrid_filename

def load_speaker(audio):
    from text.models import Speaker
    if audio.language.language == 'Hungarian':
        return Speaker.objects.get(identifier=1)
    audio_filename = Path(audio.filename).name
    speaker_id = load_mls_speakers.audio_filename_to_speaker_id(audio_filename)
    speaker = Speaker.objects.get(identifier=speaker_id)
    return speaker
    
def load_in_maus_textgrid(audio,mls_root_folder,dataset):
    from text.models import Textgrid 
    filename = get_maus_textgrid_filename(audio.filename, mls_root_folder)
    if not Path(filename).exists():
        print('no textgrid file',filename, 'for',audio.filename, 'skipping')
        return None
    speaker = load_speaker(audio)
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

def handle_language(language_name):
    from text.models import Audio
    mls_root_folder = locations.get_language_mls_root_folder(language_name)
    language = load_mls_audio.load_language(language_name)
    dataset = load_mls_audio.load_dataset('MLS')
    audios = Audio.objects.filter(language=language, dataset=dataset)
    n_created = 0
    error = 0
    for audio in progressbar(audios):
        created = load_in_maus_textgrid(audio, mls_root_folder, dataset)
        if created is None: error += 1
        elif created: n_created += 1
    print('created',n_created, 'textgrids for',language_name, 
        'no file for',error)



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



