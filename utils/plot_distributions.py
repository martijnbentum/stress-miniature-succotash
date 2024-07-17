from matplotlib import pyplot as plt

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
