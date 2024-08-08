import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import re

def scale(hidden_states):
    '''scale hidden states
    '''
    scaler = StandardScaler()
    return scaler.fit_transform(hidden_states)

def pca(hidden_states, n_components = 50, scale = False):
    '''principal component analysis
    '''
    if scale:
        hidden_states = scale(hidden_states)
    pca = PCA(n_components = n_components)
    return pca.fit_transform(hidden_states)

def tsne(hidden_states, perplexity = 30, n_iter = 1000, random_state = 0,
    apply_pca = False, pca_components = 50, scale_before_pca = False):
    '''t-distributed stochastic neighbor embedding
    '''
    if apply_pca:
        hidden_states = pca(hidden_states, n_components = pca_components, 
            scale = scale_before_pca)
    tsne = TSNE(n_components=2, perplexity=perplexity, n_iter=n_iter, 
        random_state=random_state)
    tsne_results = tsne.fit_transform(hidden_states)
    return tsne_results

def plot_tsne(tsne_hidden_states, labels = None, label_dict = None,
    marker_dict = None, title = '', add_legend = True, legend_outside = False,
    ax = None):
    '''plot t-distributed stochastic neighbor embedding
    '''
    title = 't-SNE ' + title
    if not ax: fig, ax = plt.subplots()
    x = tsne_hidden_states[:,0]
    y = tsne_hidden_states[:,1]
    colors = plt.cm.tab20.colors
    print('n tokens', len(y), 'n labels', len(set(labels)))
    if len(label_dict) > len(colors):
        colors = np.vstack((colors, plt.cm.tab20b.colors, plt.cm.tab20c.colors))
    n = np.array(labels)
    for label in label_dict.keys():
        if label_dict:
            label_name = label_dict[label]
        else:
            label_name = label
        if marker_dict:
            marker = marker_dict[label]
        else:
            marker = 'o'
        color = colors[label]
        print(label, label_name, color, marker)
        index = np.where(n == label)
        scatter = ax.scatter(x[index], y[index], label = label_name, 
            color = color, marker = marker)
    if add_legend:
        if legend_outside:
            ax.legend(title = 'Classes', bbox_to_anchor=(1.05, 1), 
               borderaxespad=0) 
        else:
            ax.legend(title = 'Classes')
    #plt.colorbar(scatter)
    ax.set_title(title)
    if not ax: 
        plt.show()
    return scatter

def old_plot_tsne(tsne_hidden_states, labels = None, label_dict = None,
    title = '', add_legend = True):
    '''plot t-distributed stochastic neighbor embedding
    '''
    title = 't-SNE' + title
    plt.figure()
    x = tsne_hidden_states[:,0]
    y = tsne_hidden_states[:,1]
    scatter = plt.scatter(x, y, c = labels, cmap = 'tab20')
    handles, labels = scatter.legend_elements()
    if label_dict:
        labels = [int(re.search(r'\d+', label).group()) for label in labels]
        labels = [label_dict[label] for label in labels]
    if add_legend:
        plt.legend(handles, labels, title = 'Classes')
    #plt.colorbar(scatter)
    plt.title(title)
    plt.show()
    return scatter

