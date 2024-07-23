from utils import select
from utils import plot_distributions

def _vowels_to_durations(vowel_stress_dict):
    d = vowel_stress_dict
    output = {}
    for k,v in d.items():
        output[k] = [x.duration for x in v]
    return output

def make_vowel_duration_stress_dict(language_name = 'dutch', 
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None):
    '''make dict mapping stress / no_stress to vowel durations'''
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    d = _vowels_to_durations(d)
    return d

def plot_stress_no_stress_distributions(durations = None, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 240, plot_density = False, xlabel = 'Duration (s)'):
    if not durations: durations = make_vowel_duration_stress_dict()
    kwargs = {
        'value_dict':durations,
        'new_figure':new_figure,
        'minimal_frame':minimal_frame,
        'ylim':ylim,
        'add_left':add_left,
        'add_legend':add_legend,
        'bins':bins,
        'xlabel':xlabel,
        'xlim':(0.02, 0.26),
        'plot_density':plot_density
        }
    plot_distributions.plot_stress_no_stress_distributions(**kwargs)
