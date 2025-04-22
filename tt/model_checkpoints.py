import glob

base_path = '/vol/mlusers/mbentum/st_phonetics/'
model_path = base_path + 'w2v2_models/'
embed_path = base_path + 'mls_1sp_embed/'
m_nl = model_path + 'wav2vec2_base_dutch_960h/'
m_en = model_path + 'model-wav2vec2_type-base_data-librispeech_version-4/'
m_ns = model_path + 'model-wav2vec2_type-base_data-audiosetfilter_version-2/'


def language_step_model_checkpoint(language, step) :
    linked_model_checkpoints = link_model_checkpoint_to_step(language)
    for line in linked_model_checkpoints:
        if line['step'] == step:
            return line['checkpoint']
    return False

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

def model_checkpoint_to_step(model_checkpoint):
    language = model_checkpoint_to_language(model_checkpoint)
    if language == 'nl':step = model_checkpoint.split('_')[-1]
    else: step = model_checkpoint.split('-')[-1]
    return int(step) 

def model_checkpoint_to_language(model_checkpoint):
    if 'dutch' in model_checkpoint:
        return 'nl'
    if 'librispeech' in model_checkpoint:
        return 'en'
    if 'audiosetfilter' in model_checkpoint:
        return 'ns'
    return False

def link_model_checkpoint_to_step(language = 'nl'):
    output = []
    model_checkpoints = get_model_checkpoints(language)
    for model_checkpoint in model_checkpoints:
        step = model_checkpoint_to_step(model_checkpoint)
        d = {'step': step, 
            'language': language, 'checkpoint': model_checkpoint}
        output.append(d)
    return output
