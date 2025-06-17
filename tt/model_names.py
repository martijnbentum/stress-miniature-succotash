from . import link_audio_to_model as latm
from . import step_list

dutch = 'nl'
english = 'en'
non_speech = 'ns'
languages = [dutch, english, non_speech]

steps = step_list.steps
try: model_names = latm.all_model_names()
except: model_names = None

hubert_base = 'hubert-base-ls960-cgn'
hubert_multilingual = 'mHuBERT-147-cgn'
wavlm_base = 'wavlm-base-plus-cgn'
wav2vec2_multilingual = 'wav2vec2-xls-r-300m-cgn'

def get_model_name(language, step):
    model_name = f'{language}-{step}-cgn'
    if model_name not in model_names:
        m = f'Model name {model_name} not found in model names'
        if language not in languages:
            m += f'\n{language} not in language set: {languages}'
        if step not in steps:
            m += f'\n{step} not in step set: {steps}'
        raise ValueError(m)
    return model_name

def select_model_set_by_language(language):
    output = []
    for model in model_names:
        if language in model:
            output.append(model)
    return output

def get_dutch_models():
    return select_model_set_by_language(dutch)

def get_english_models():
    return select_model_set_by_language(english)

def get_non_speech_models():
    return select_model_set_by_language(non_speech)
            
def down_sample_model_set(model_set, n_models = 3):
    if n_models >= len(model_set):
        return model_set  

    n = len(model_set)
    indices = [n - 1, 0]  # Start with last and first element

    if n_models > 2:
        remaining_slots = n_models - 2
        step = n / (remaining_slots + 1)  # Divide as evenly as possible

        for i in range(1, remaining_slots + 1):
            indices.append(round(i * step))

    return [model_set[i] for i in sorted(set(indices))]





