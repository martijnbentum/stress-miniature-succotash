from utils import locations
from utils import load_hidden_states as lhs
from utils import select
import numpy as np
from pathlib import Path
import pickle
from progressbar import progressbar
import random

tf_layers = lhs.hidden_state_indices

class HiddenStates:
    def __init__(self, items, items_attribute_name = 'items',
        item_to_hidden_states = None,
        item_to_ground_truth = None, 
        ground_truth_dict = None,
        name = 'default',
        model = 'wav2vec2-xls-r-300m'): 
        setattr(self, items_attribute_name, items)
        self.set_items_attribute_name(items_attribute_name)
        if not item_to_hidden_states: item_to_hidden_states = get_hidden_states
        self.item_to_hidden_states = item_to_hidden_states
        self.item_to_ground_truth = item_to_ground_truth
        self.ground_truth_dict = ground_truth_dict
        self.name = name
        self.model = model

    def get_items(self):
        return getattr(self, self.items_attribute_name)

    def set_items_attribute_name(self, items_attribute_name):
        if not hasattr(self, 'items_attribute_name'):
            self.items_attribute_name = items_attribute_name
            self.items_attribute_names = []
        if not items_attribute_name: return
        if not hasattr(self, items_attribute_name):
            em = f'items_attribute_name {items_attribute_name} not found'
            raise ValueError(em)
        if self.items_attribute_name not in self.items_attribute_names:
            self.items_attribute_names.append(self.items_attribute_name)
        self.items_attribute_name = items_attribute_name

    def _xy(self, item, layer):
        if not self.item_to_ground_truth: return None, None
        x = self.item_to_hidden_states(item, layer)
        if x is None: return None, None
        y = self.item_to_ground_truth(item, self.ground_truth_dict)
        if y is None: return None, None
        return x, y

    def xy(self, layer = 'cnn', n = None, random_ground_truth = False,
        items_attribute_name = None):
        self.set_items_attribute_name(items_attribute_name)
        items = self.get_items()
        if n: items = random.sample(items, n)
        x_values, y_values = [], []
        for item in progressbar(items):
            x, y = self._xy(item, layer)
            if x is None: continue
            x_values.append(x)
            y_values.append(y)
        return np.array(x_values), np.array(y_values)


class StressInfo(HiddenStates):
    def __init__(self, syllables, dataset_name = 'default', 
        model = 'wav2vec2-xls-r-300m', 
        skip_syllables_with_multiple_vowels = False,
        use_multiple_vowels = False):
        '''Initialize StressInfo object to extract hiddenstates from syllables.
        the class can be used to create a dataset of hiddenstates based on 
        stress status
        the input can be syllables or the onset vowel rime coda of a syllable.
        syllables:          list of syllables as defined in text.models.
        dataset_name:       name of the dataset.
        model:              name of the asr model which outputed the 
                            hiddenstates.
        skip_syllables...:  if True, syllables with multiple vowels are skipped.
        use_multiple_v...:  if True and a syllable has multiple vowels 
                            they are all used as input.
        '''
        self.ground_truth_dict = {False: 0, True: 1}
        super().__init__(syllables, item_to_ground_truth = item_to_stress,
            items_attribute_name = 'syllables', 
            ground_truth_dict = self.ground_truth_dict )
        self.dataset_name = dataset_name
        self.model = model
        self.skip_multiple_vowels = skip_syllables_with_multiple_vowels
        self.use_multiple_vowels = use_multiple_vowels
        self._set_info()

    def _set_info(self):
        pass

    def _handle_section_items(self, section, name):
        print(f'handling {section} items')
        if not hasattr(self, name): 
            setattr(self, name, [])
            items = getattr(self, name)
            for syllable in progressbar(self.syllables):
                item = getattr(syllable, section)
                if not item: continue
                items.append(item)
        self.items_attribute_name = name

    def _set_get_hidden_state_function(self, section):
        if section == 'syllable':
            self.item_to_hidden_states = get_hidden_states
        if section in ['onset', 'vowel','rime', 'coda']:
            self.item_to_hidden_states = get_hidden_states_multiple_phonemes

    def _handle_section(self, section):
        if section not in ['onset','vowel','rime','coda','syllable']:
            me = 'section must be either onset vowel rime coda or syllable'
            raise ValueError(me)
        name = section + 's'
        self._handle_section_items(section, name)
        self._set_get_hidden_state_function(section)
        

    def xy(self, layer = 'cnn', section = 'syllable', n = None,
        random_ground_truth = False):
        self._handle_section(section)
        return super().xy(layer, n, random_ground_truth, 
            self.items_attribute_name)
            
def get_attribute_name(name):
    if name == 'cnn': return 'cnn'
    if type(name) == int and name in tf_layers:
        return 'transformer'

def get_parameters(name):
    kwargs = {'mean': True}
    if name == 'cnn': return kwargs
    if type(name) == int and name in tf_layers:
        kwargs['layer'] = name
        return kwargs

def get_hidden_states(item, layer):
    attribute_name = get_attribute_name(layer)
    parameters = get_parameters(layer)
    attribute = getattr(item, attribute_name)
    return attribute(**parameters)

def get_hidden_states_multiple_phonemes(phonemes, layer):
    if not type(phonemes) == list: phonemes = [phonemes]
    o = lhs.phoneme_list_to_combined_hidden_states(phonemes, hs = layer, 
        mean = True)
    return o
    

def item_to_stress(item, ground_truth_dict):
    if type(item) == list: item = item[0]
    return ground_truth_dict[item.stress]

def item_to_word_type(item, ground_truth_dict):
    return ground_truth_dict[item.word]

def item_to_syllable_type(item, ground_truth_dict):
    return ground_truth_dict[item.ipa]

def syllable_to_vowel(syllable, skip_multiple_vowels = False):
    if skip_multiple_vowels and len(syllable.vowel) > 1:
        return None
    if not syllable.vowel: return None
    return syllable.vowel[0]

def handle_language_stress_info(language_name, si = None, sections = [],
    layers = [], name = ''):
    if not sections: sections = ['vowel']
    if not layers: layers = ['codevector','cnn', 5,11,17,23]
    if si is None: 
        print('selecting syllables')
        syllables = select.select_syllables(language_name, 
            number_of_syllables = 2)
        print('creating StressInfo object')
        si = StressInfo(syllables)
    for section in sections:
        for layer in layers:
            print(f'handling {section} {layer}')
            filename = make_dataset_filename(language_name, layer, section, 
                name)
            path = Path(filename)
            if path.exists(): 
                print(f'file {filename} exists. skipping')
                continue
            X, y = si.xy(layer = layer, section = section)
            save_xy(X, y, language_name, section = section, layer = layer,
                name = name)
    return si

def make_dataset_filename(language_name, layer, section, name = '', n = ''):
    from utils import perceptron
    data_type = 'stress'
    return perceptron.make_dataset_filename(language_name, data_type, layer,
        section, name, n)
        


def save_xy(X, y, language_name, section = '', layer = '', n = '', name = ''):
    d = {'X': X, 'y': y, 'section': section, 'layer': layer, 'n': n, 
        'language_name': language_name, 'name': name}
    '''
    filename = f'../dataset/xy_dataset-stress_language-{language_name}_'
    filename += f'section-{section}_layer-{layer}_n-{n}_name-{name}.pickle'
    '''
    filename = make_dataset_filename(language_name, layer, section, name, n)
        
    with open(filename, 'wb') as f:
        pickle.dump(d, f)

def move_from_data_to_dataset():
    import glob
    from pathlib import Path
    fn = glob.glob('../data/xy_*.pickle')
    for f in fn:
        if not 'vowel' in f: continue
        new_f = f.replace('data', 'dataset')
        new_f = new_f.replace('xy_', 'xy_dataset-stress_')
        p = Path(new_f)
        if p.exists(): 
            print('file exists',new_f, 'skipping')
            print('-')
            continue
        print('moving',f,'to',new_f)
        with open(f, 'rb') as fout:
            d = pickle.load(fout)
        print(d)
        d['data_type'] = 'stress'
        print(d)
        with open(new_f, 'wb') as fout:
            pickle.dump(d, fout)
        print('done')
        print('-')
    return fn
