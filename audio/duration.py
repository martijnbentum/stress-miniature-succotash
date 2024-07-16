from matplotlib import pyplot as plt
from progressbar import progressbar
from utils import select

def collect_vowels(language_name, 
    dataset_name = 'COMMON VOICE', minimum_n_syllables = 2,
    max_n_items_per_speaker = None):
    '''
    Collects the stress and no stress vowels for a given language.
    '''
    print('creating query set, for language:',language_name)
    print('dataset:',dataset_name,'minimum_n_syllables:',minimum_n_syllables)
    vowels = select.select_phonemes(language_name = language_name,
        dataset_name = dataset_name, minimum_n_syllables = minimum_n_syllables,
        bpc_name = 'vowel')
    print('query set created, now collecting stress and no stress vowels')
    d = sort_vowels_based_on_stress(vowels)
    return d

def sort_vowels_based_on_stress(vowels):
    d = {'stress':[],'no_stress':[]}
    for vowel in vowels:
        if vowel.stress:d['stress'].append(vowel)
        else:d['no_stress'].append(vowel)
    return d

def collect_stress_no_stress_durations(d = None):
    if not d:
        d = collect_stress_no_stress_vowels('dutch')
    output = {}
    for k,v in d.items():
        output[k] = [x.duration for x in v]
    return output

def plot_stress_no_stress_distributions(durations = None, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380):
    if not durations: collect_stress_no_stress_durations()
    plt.ion()
    if new_figure: plt.figure()
    ax = plt.gca()
    if minimal_frame:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    if ylim: plt.ylim(ylim)
    plt.xlim(0.02, 0.26)
    plt.hist(durations['stress'], bins=bins, color = 'black', alpha=1,
        label='stress')
    plt.hist(durations['no_stress'], bins=bins, color = 'orange', alpha=.7,
        label='no stress')
    if add_legend: plt.legend()
    plt.xlabel('Duration (s)')
    if add_left: plt.ylabel('Counts')
    else:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left = False)
        ax.set_yticklabels([])
    plt.grid(alpha=0.3)
