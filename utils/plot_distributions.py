from matplotlib import pyplot as plt
from audio import duration
from audio import formants
from audio import frequency_band
from audio import intensity
from audio import pitch

# circular imports for duration formants frequency_band intensity pitch
# not sure if this is a major issue
   

def plot_stress_no_stress_distributions(value_dict, new_figure = True,
    minimal_frame = False, ylim = None, add_left = True, add_legend = True, 
    bins = 380, xlabel = '', xlim = None):
    '''plot the stress and no stress distributions of a given value_dict
    dict should contain stress no_stress keys with lists of values 
    (e.g. duration)
    '''
    d = value_dict
    plt.ion()
    if new_figure: plt.figure()
    ax = plt.gca()
    if minimal_frame:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    if ylim: plt.ylim(ylim)
    if xlim: plt.xlim(xlim)
    plt.hist(d['stress'], bins=bins, color = 'black', alpha=1,
        label='stress')
    plt.hist(d['no_stress'], bins=bins, color = 'orange', alpha=.7,
        label='no stress')
    if add_legend: plt.legend()
    plt.xlabel(xlabel)
    if add_left: plt.ylabel('Counts')
    else:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left = False)
        ax.set_yticklabels([])
    plt.grid(alpha=0.3)

def get_all_data(language_name = 'dutch', dataset_name = 'COMMON VOICE',
    minimum_n_syllables = 2, max_n_items_per_speaker = None,
    vowel_stress_dict = None):
    if not vowel_stress_dict:
        d = select.select_vowels(language_name, dataset_name,
            minimum_n_syllables, max_n_items_per_speaker, 
            return_stress_dict = True)
    else: d = vowel_stress_dict
    print('Processing durations')
    durations = duration.make_vowel_duration_stress_dict(vowel_stress_dict = d)
    print('Processing formants')
    formant = formants.make_vowel_f1f2_distance_stress_dict(vowel_stress_dict=d)
    print('Processing spectral tilt')
    X,y = frequency_band.make_dataset(vowel_stress_dict = d)
    clf, _, _ = frequency_band.train_lda(X, y, report = False)
    print('Processing intensities')
    intensities=intensity.make_vowel_intensity_stress_dict(vowel_stress_dict=d)
    print('Processing pitch')
    pitch_values = pitch.make_vowel_pitch_stress_dict(vowel_stress_dict=d)
    data = {
        'durations': durations,
        'formants': formant,
        'spectral_tilt': (X, y, clf),
        'intensities': intensities,
        'pitch': pitch_values,
        }
    return data

def plot_all_acoustic_features(language_name = 'dutch',
    dataset_name = 'COMMON VOICE',minimum_n_syllables = 2,
    max_n_items_per_speaker = None, vowel_stress_dict = None, 
    ylim = (0,50_000), data = None, row_index = 1, nrows = 1, 
    new_figure = True):
    '''plot all acoustic features'''
    if not data:
        data = get_all_data(language_name, dataset_name, minimum_n_syllables,
            max_n_items_per_speaker, vowel_stress_dict)
    plt.ion()
    if new_figure: plt.figure()
    plot_index = row_index * 5 - 5
    print('plot index', plot_index)
    plt.subplot(nrows,5,plot_index + 1)
    intensity.plot_stress_no_stress_distributions(data['intensities'],
        new_figure = False, minimal_frame = True, 
        add_legend = False, ylim = ylim )
    plt.subplot(nrows,5,plot_index +2)
    duration.plot_stress_no_stress_distributions(data['durations'],
        new_figure = False, minimal_frame = True, 
        add_left = False, add_legend = False, ylim = ylim )
    plt.subplot(nrows,5,plot_index + 3)
    formants.plot_stress_no_stress_distributions(data['formants'],
        new_figure = False, minimal_frame = True, 
        add_left = False, add_legend = False, ylim = ylim )
    plt.subplot(nrows,5,plot_index + 4)
    pitch.plot_stress_no_stress_distributions(data['pitch'],
        new_figure = False, minimal_frame = True, 
        add_left = False, add_legend = False, ylim = ylim )
    plt.subplot(nrows,5,plot_index + 5)
    frequency_band.plot_lda_hist(*data['spectral_tilt'],
        new_figure = False, minimal_frame = True, 
        add_left = False, add_legend = True, ylim = ylim )
    return data

    
    
    
    
    
