import json
import glob
from w2v2_hidden_states import load
import pickle
import torch
from . import link_audio_to_model, step_list

base_path = '/vol/mlusers/mbentum/st_phonetics/'
model_path = base_path + 'w2v2_models/'
embed_path = base_path + 'mls_1sp_embed/'
m_nl = model_path + 'wav2vec2_base_dutch_960h/'
m_en = model_path + 'model-wav2vec2_type-base_data-librispeech_version-4/'
m_ns = model_path + 'model-wav2vec2_type-base_data-audiosetfilter_version-2/'

emb_nl = embed_path + 'w2v2-nl/'
emb_en = embed_path + 'w2v2-en/'
emb_ns = embed_path + 'w2v2-ns/'

codebook_path = base_path + 'codebooks/'

steps = step_list.steps[:]

def audio_language_model_checkpoints_of_missing_steps(audio, language = 'nl'):
    missing_steps = audio_language_to_missing_steps(audio, language)
    linked_models_and_embeds = link_models_and_embeds(language)
    lme = linked_models_and_embeds
    model_infos = [step_to_model(s, language, lme) for s in missing_steps]
    checkpoints = [x['model'] for x in model_infos]
    return checkpoints

def audio_language_to_missing_steps(audio, language = 'nl'):
    d = link_audio_to_model.make_audio_hidden_state_model_field_dict(audio)
    finished_steps = d[language]
    missing_steps = list(set(steps) - set(finished_steps))
    return missing_steps
    
def step_to_model(step, language='nl', linked_models_and_embeds = None):
    if not linked_models_and_embeds:
        linked_models_and_embeds = link_models_and_embeds(language)
    for line in linked_models_and_embeds:
        if line['step'] == step:
            return line
    return False

def handle_language(language):
    o = link_models_and_embeds(language)
    cis = []
    for i,line in enumerate(o):
        print(i,len(o))
        ci = handle_linked_models_and_embeds_line(line)
        cis.append(ci)

def handle_linked_models_and_embeds_line(line):
    '''handle a line from the linked_models_and_embeds output'''
    step = line['step']
    language = line['language']
    model_checkpoint = line['model']
    embed_filename = line['embed']
    print(f'Processing {step} with language: {language}')
    print(f'Processing {model_checkpoint} with {embed_filename}')
    model = load_model_pt(model_checkpoint)
    embed = load_embed(embed_filename)
    cnn = embed['CNN']
    codebook_filename = make_codebook_filename(model_checkpoint)
    codebook_indices = map_to_codebook_indices(cnn, model)
    save_json(codebook_indices, codebook_filename)
    return codebook_indices

def make_codebook_filename(model_checkpoint):
    language = model_to_language(model_checkpoint)
    step = model_to_step(model_checkpoint)
    filename = codebook_path + f'codebook_{language}_{step}.json'
    return filename

def load_model_pt(checkpoint = None, gpu = False):
    '''wrapper function to load the model_pt'''
    return load.load_model_pt(checkpoint, gpu)

def load_pretrained_model(checkpoint = None,gpu = False):
    '''wrapper function to load the pretrained model'''
    return load.load_pretrained_model(checkpoint, gpu)

def load_embed(embed_file):
    with open(embed_file, 'rb') as f:
        embed = pickle.load(f)
    return embed

def map_to_codebook_indices(cnn, model_pt):
    cis = codebook.cnn_output_to_codebook_indices(cnn, model_pt)
    cis = [tuple(map(int, x)) for x in cis]
    return cis

def link_models_and_embeds(language = 'nl'):
    output = []
    model_checkpoints = get_model_checkpoints(language)
    for model_checkpoint in model_checkpoints:
        embed = model_to_embed(model_checkpoint)
        step = model_to_step(model_checkpoint)
        if not embed: 
            print(f'Embed not found for {model_checkpoint}, skipping...')
            continue
        d = {'embed': embed, 'step': step, 
            'language': language, 'model': model_checkpoint}
        output.append(d)
    return output

def get_model_checkpoints(language='nl'):
    if language == 'nl':
        dirs = glob.glob(m_nl + '*')
        return [x for x in dirs if not 'last' in x and not 'best' in x]
    if language == 'en':
        dirs = glob.glob(m_en + '*')
        return [x for x in dirs if not 'initialmodel' in x] 
    if language == 'ns':
        dirs = glob.glob(m_ns + '*')
        return [x for x in dirs if not 'initialmodel' in x] 
    return False

def get_embeds(language='nl'):
    if language == 'nl':
        return glob.glob(emb_nl + '*.pkl')
    if language == 'en':
        return glob.glob(emb_en + '*.pkl')
    if language == 'ns':
        return glob.glob(emb_ns + '*.pkl')
    return False

def model_to_identifier(model_checkpoint):
    return model_checkpoint.split('checkpoint')[-1]

def embed_to_identifier(embed_file):
    return embed_file.split('checkpoint')[-1].split('.')[0]

def model_to_language(model_checkpoint):
    if 'dutch' in model_checkpoint:
        return 'nl'
    if 'librispeech' in model_checkpoint:
        return 'en'
    if 'audiosetfilter' in model_checkpoint:
        return 'ns'
    return False

def model_to_step(model_checkpoint):
    language = model_to_language(model_checkpoint)
    if language == 'nl':step = model_checkpoint.split('_')[-1]
    else: step = model_checkpoint.split('-')[-1]
    return int(step) 

def model_to_embed(model_checkpoint):
    language = model_to_language(model_checkpoint)
    embeds = get_embeds(language)
    model_id = model_to_identifier(model_checkpoint)
    for embed in embeds:
        embed_id = embed_to_identifier(embed)
        if model_id == embed_id:
            return embed
    return False

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
