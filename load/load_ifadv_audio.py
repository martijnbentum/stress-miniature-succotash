import json
from load import load_cv_speakers 
from pathlib import Path
from progressbar import progressbar
from audio import audio
from utils import locations
from utils import overlap

def audio_to_overlapping_audio(audio, audios):
    overlap_ids = []
    info = json.loads(audio.info)
    dialogue_id = info['dialogue_id']
    for other_audio in audios:
        if audio == other_audio: continue
        other_info = json.loads(other_audio.info)
        if dialogue_id != other_info['dialogue_id']: continue
        if info['speaker_id'] == other_info['speaker_id']: 
            continue
        s1, e1 = audio_to_dialogue_start_end_times(audio, info)
        s2, e2 = audio_to_dialogue_start_end_times(other_audio, other_info)
        if overlap.overlap(s1,e1,s2,e2):
            overlap_ids.append(other_audio.identifier)
    return overlap_ids

def audio_to_dialogue_start_end_times(audio, info = None):
    if not info: 
        info = json.loads(audio.info)
    start_time = info['start_time']
    end_time = start_time + audio.duration
    return start_time, end_time

def _update_turn_index(filename, index_modifier = -1):
    f = filename.split('/')[-1]
    turn_index = int(f.split('_ti-')[-1].split('_')[0])
    new_turn_index = turn_index + index_modifier
    filename = f.replace(f'_ti-{turn_index}_',f'_ti-{new_turn_index}_')
    partial_filename = filename.split('ch-')[0]
    return partial_filename

def audio_to_previous_audio(audio):
    from text.models import Audio
    filename = _update_turn_index(audio.filename, index_modifier = -1)
    print(audio.filename, filename)
    try: previous_audio = Audio.objects.get(filename__icontains=filename)
    except Audio.DoesNotExist: return None
    return previous_audio

def audio_to_next_audio(audio):
    from text.models import Audio
    filename = _update_turn_index(audio.filename, index_modifier = 1)
    print(audio.filename, filename)
    try: next_audio = Audio.objects.get(filename__icontains=filename)
    except Audio.DoesNotExist: return None
    return next_audio

def audio_to_neighbouring_audios(audio):
    previous_audio = audio_to_previous_audio(audio)
    next_audio = audio_to_next_audio(audio)
    return previous_audio, next_audio

def load_wav_filename_to_overlap_dict():
    filename = locations.ifadv_audio_file_to_overlap
    with open(filename) as f:
        d = json.load(f)
    return d

def load_wav_filename_to_start_time_dict():
    filename = locations.ifadv_audio_file_to_start_time
    with open(filename) as f:
        d = json.load(f)
    return d

def load_wav_filename_to_speaker_id_dict():
    filename = locations.ifadv_audio_file_to_speaker_id
    with open(filename) as f:
        d = json.load(f)
    return d

def audio_filename_to_dialogue_id(audio_filename):
    temp = Path(audio_filename).stem 
    dialogue_id = temp.split('_')[0]
    return dialogue_id

def audio_filename_to_speaker_id(audio_filename, speaker_dict = None):
    if not speaker_dict:
        speaker_dict = load_wav_filename_to_speaker_id_dict()
    filename = audio_filename
    if not filename in speaker_dict.keys(): return None
    speaker_id = speaker_dict[filename]
    return speaker_id

def dialogue_id_to_speaker_ids_dict(speaker_dict = None):
    if not speaker_dict:
        speaker_dict = load_wav_filename_to_speaker_id_dict()
    d = {}
    for turn_wav_filename, speaker_id in speaker_dict.items():
        dialogue_id = Path(turn_wav_filename).stem.split('_')[0]
        if not dialogue_id in d.keys():
            d[dialogue_id] = []
        if speaker_id not in d[dialogue_id]:
            d[dialogue_id].append(speaker_id)
    return d

def make_info_dict_for_audio(audio_filename, speaker_dict = None,
    start_time_dict = None, overlap_dict = None):
    if not speaker_dict:
        speaker_dict = load_wav_filename_to_speaker_id_dict()
    if not start_time_dict:
        start_time_dict = load_wav_filename_to_start_time_dict()
    info = {}
    dialogue_id = audio_filename_to_dialogue_id(audio_filename)
    info['dialogue_id'] = dialogue_id
    speaker_id= audio_filename_to_speaker_id(audio_filename, speaker_dict)
    info['speaker_id'] = speaker_id
    speaker_ids = dialogue_id_to_speaker_ids_dict(speaker_dict)[dialogue_id]
    info['speaker_ids'] = speaker_ids
    other_speaker_id = [sid for sid in speaker_ids if sid != speaker_id][0]
    info['other_speaker_id'] = other_speaker_id
    info['start_time'] = start_time_dict[audio_filename]
    info['overlap'] = overlap_dict[audio_filename]
    return info

def load_dataset(dataset_name):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset

def load_language(language_name):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language

def handle_audio_file(file_info, language, dataset, speaker_dict = None):
    from text.models import Audio, Dataset, Language
    filename = file_info['filename']
    path = Path(filename)
    identifier = file_info['identifier']
    try: d = audio.soxinfo_to_dict(audio.soxi_info(filename))
    except: 
        print('Error with',filename)
        return False
    info_dict = make_info_dict_for_audio(filename, speaker_dict)
    d['info'] = json.dumps(info_dict)
    d['identifier'] = identifier
    d['language'] = language
    d['dataset'] = dataset
    audio, created = Audio.objects.get_or_create(**d)
    if not created:
        if not audio.info == d['info']:
            audio.info = d['info']
            audio.save()
    return created


def get_audio_files():
    fn = locations.ifadv_audio.glob('*.wav')
    audio_files = []
    for f in fn:
        audio_files.append(f)
    audio_files = [{'filename':f,'identifier':f.stem, 'language':'dutch'} 
        for f in audio_files]
    return audio_files

def handle_all_audio_files():
    print('handling audio files of the ifdav dataset')
    language = load_language('dutch')
    dataset = load_dataset('IFADV')
    speaker_dict = load_wav_filename_to_speaker_id_dict()
    audio_files = get_audio_files()
    n_created = 0
    for f in progressbar(audio_files):
        created = handle_audio_file(f, language, dataset, speaker_dict)
        if created: n_created += 1
    print('created',n_created,'new audio instances for the ifadv dataset')


def add_info_dict_to_audios(audios):
    error = []
    speaker_dict = load_wav_filename_to_speaker_id_dict()
    start_time_dict = load_wav_filename_to_start_time_dict()
    overlap_dict = load_wav_filename_to_overlap_dict()
    for audio in progressbar(audios):
        info_dict = make_info_dict_for_audio(audio.filename, speaker_dict,
            start_time_dict, overlap_dict)
        if not info_dict: 
            error.append(audio)
            continue
        audio.info = json.dumps(info_dict)
        audio.save()
    return error

def add_overlap_ids_to_info_dict(audios):
    for audio in progressbar(audios):
        overlap_ids = audio_to_overlapping_audio(audio, audios)
        info = json.loads(audio.info)
        info['overlap_ids'] = overlap_ids
        audio.info = json.dumps(info)
        audio.save()

