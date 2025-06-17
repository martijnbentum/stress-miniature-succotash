# applied different models to cgn some links got overwritten

import glob
import json
from tt import step_list, select_materials
from utils import locations
from text.models import Audio

extra_model_names = 'hubert-base-ls960-cgn,mHuBERT-147-cgn,'
extra_model_names += 'wavlm-base-plus-cgn,wav2vec2-xls-r-300m-cgn'

steps = step_list.steps
languages = ['nl','ns','en']

def all_model_names():
    o =hidden_state_number_dict_to_hidden_state_model_names_dict()
    temp = list(o.values())[0]
    model_names = [x.split('_')[1] for x in temp]
    return model_names

def audio_language_step_to_hidden_state_model_name(audio, language, step):
    number = audio_to_hidden_state_number(audio)
    return make_hidden_state_model_item(number, language, step)

def hidden_state_number_dict_to_hidden_state_model_names_dict(d = None, 
    languages = ['nl','ns','en']):
    if d is None:
        d = make_or_load_audio_to_hidden_state_number_dict()
    steps = step_list.steps
    output = {}
    for audio_id, number in d.items():
        output[audio_id] = []
        for language in languages:
            for step in steps:
                item = make_hidden_state_model_item(number, language, step)
                output[audio_id].append(item)
        for model_name in extra_model_names.split(','):
            output[audio_id].append(f'{number}_{model_name}')
    return output
    

def audio_to_steps(audio):
    infos = audio_hidden_state_model_to_infos(audio)
    steps = sorted([info['step'] for info in infos])
    return steps

def make_or_load_audio_to_hidden_state_number_dict(audios=None):
    dict_path = locations.st_phonetics_audio_to_hidden_state_number_dict
    if dict_path.exists() and audios is None:
        with dict_path.open() as f:
            d = json.load(f)
        return d
    if not audios: audios = select_materials.load_audios()
    d = {}
    for x in audios:
        d[x.identifier] = audio_to_hidden_state_number(x)
    with dict_path.open('w') as f:
        json.dump(d,f)
    return d

def audio_to_hidden_state_number(audio):
    infos = audio_hidden_state_model_to_infos(audio)
    numbers = [info['data_filenumber'] for info in infos]
    number = list(set(numbers))
    if len(number) > 1:
        raise ValueError('audio has multiple data_filenumbers', number)
    number = number[0]
    return number
    
def audios_to_current_hidden_state_model_names(audios, filename = ''):
    d = {}
    for x in audios:
        d[x.identifier] = x.hidden_state_model
    if filename:
        with open(filename, 'w') as f:
            json.dump(d,f)
    return d

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
        

    
