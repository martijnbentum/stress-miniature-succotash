# applied different models to cgn some links got overwritten

import glob
from utils import locations
from text.models import Audio

def get_model_folders():
    dirs = glob.glob(str(locations.hidden_states_dir) + '/*cgn*')
    return dirs

def dir_to_step(f):
    return int(f.split('-')[-2])

def dir_to_language(f):
    return f.split('-')[-3].split('/')[-1]

def make_model_dict():
    dirs = get_model_folders()
    d = {}
    for f in dirs:
        language = dir_to_language(f)
        step = dir_to_step(f)
        if language not in d:
            d[language] = [step]
        else:
            d[language].append(step)
    return d

def audio_hidden_state_model_to_info(name):
    d = {}
    d['data_filenumber'] = int(name.split('_')[0])
    d['language'] = name.split('_')[1].split('-')[0]
    d['step'] = int(name.split('-')[-2])
    return d

def audio_hidden_state_model_to_infos(audio):
    infos = []
    for item in audio.hidden_state_model.split(','):
        info = audio_hidden_state_model_to_info(item)
        infos.append(info)
    return infos

def make_audio_hidden_state_model_field_dict(audio):
    infos = audio_hidden_state_model_to_infos(audio)
    d = {}
    for info in infos:
        if info['language'] not in d:
            d[info['language']] = [info['step']]
        else:
            d[info['language']].append(info['step'])
    return d

def make_missing_dict(audio):
    md = make_model_dict()
    ad = make_audio_hidden_state_model_field_dict(audio)
    diff = {}
    for language in md:
        if language not in ad:
            diff[language] = md[language]
        else:
            diff[language] = list(set(md[language]) - set(ad[language]))
    return diff

def handle_audio(audio,save=False):
    infos = audio_hidden_state_model_to_infos(audio)
    data_filenumbers = [info['data_filenumber'] for info in infos]
    if not len(list(set(data_filenumbers))) == 1:
        print('audio has multiple data_filenumbers', list(set(data_filenumbers)))
        return
    data_filenumber = data_filenumbers[0]
    missing = make_missing_dict(audio)
    field = audio.hidden_state_model
    for language in missing:
        for step in missing[language]:
            item = make_hidden_state_model_item(data_filenumber, language, step)
            field += f',{item}'
    if field == audio.hidden_state_model:
        print('no changes')
        return 
    if save:
        audio.hidden_state_model = field
        audio.save()
    return field

def make_hidden_state_model_item(data_filenumber, language, step):
    return f'{data_filenumber}_{language}-{step}-cgn'
        

    
