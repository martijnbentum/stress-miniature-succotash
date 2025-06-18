import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors, cm
from matplotlib.colorbar import ColorbarBase
import os
import pickle
from progressbar import progressbar
from sklearn.metrics.pairwise import cosine_distances
from sklearn.manifold import MDS
from .step_list import steps
from .general import flatten_list
from . import select_materials
from . import compute_codevectors as cc
from . import analyze_codebook
import matplotlib.colors as mcolors

def initialize_matrix(n_rows = 32, n_cols = 20):
    """Initialize a matrix with random values.
    the last dimension is for the rgba color channel.
    """
    return np.zeros((n_rows, n_cols, 4))

def get_cmap_and_norm(cmap_name='viridis', steps = steps):
    """Compute a color map based on the given name and steps."""
    norm = colors.Normalize(vmin=min(steps), vmax=max(steps))
    cmap = cm.get_cmap(cmap_name)
    return cmap, norm

def compute_rgba(cmap, norm, step, alpha=.05):
    """Compute the RGBA color for a given step."""
    rgba = list(cmap(norm(step)))
    rgba[3] = alpha
    return rgba

def update_matrix(matrix, row, col, rgba):
    """Update the matrix with a new value at the specified row and column."""
    base = matrix[row, col]
    new = rgba
    matrix[row, col] = [
        base[0]*(1-new[3]) + new[0]*new[3],
        base[1]*(1-new[3]) + new[1]*new[3],
        base[2]*(1-new[3]) + new[2]*new[3],
        min(1.0, base[3] + new[3])  # Cap max alpha
    ]
    return matrix

def _compute_row_col_indices(index, matrix, index_mapper = None):
    if index_mapper is None:
        row = index // matrix.shape[1]
        col = index % matrix.shape[1]
        return row, col
    return index_mapper[index]

def _handle_token(token, step, matrix, cmap, norm, alpha, index_mapper = None):
    indices = flatten_list(token)
    for index in indices:
        row, col = _compute_row_col_indices(index, matrix, index_mapper)
        rgba = compute_rgba(cmap, norm, step, alpha)
        matrix = update_matrix(matrix, row, col, rgba)

def compute_matrix(d = None, phoneme = 't', limit = 1000, alpha = 0.01, 
    cmap_name='viridis', steps = steps, n_rows = 32, n_cols = 20,
    codebook = None, do_load_codebook = None, index_mapper = None, 
    step = None,):
    if d is None:
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
    if codebook is not None or do_load_codebook: 
        if codebook is None and index_mapper is None: 
            codebook = cc.language_step_to_codebook('nl',step)
        if index_mapper is None:
            index_mapper = analyze_codebook.compute_index_mapper(codebook)
    matrix = initialize_matrix(n_rows, n_cols)
    cmap, norm = get_cmap_and_norm(cmap_name, steps)
    for model_name, tokens in d[phoneme].items():
        step = int(model_name.split('-')[1])
        if step not in steps:
            continue
        for token in tokens[:limit]:
            _handle_token(token, step, matrix, cmap, norm, alpha, index_mapper)
    return matrix, cmap, norm

def plot_matrix(matrix, cmap, norm):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(matrix, interpolation='nearest')
    ax.set_title("Codevector Usage Over Training")
    # ax.axis("off")
    # cb = ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')
    # cb.set_label('training Step')
    plt.show()


def add_distant_dummy_points(mds_coords, dummy_points=None,):
    if dummy_points is None:
        dummy_points=np.array([[999,999], [-999,999], [999,-999], [-999,-999]])
    mds_coords = np.append(mds_coords, dummy_points, axis=0)
    return mds_coords

def _old_codevector_index_to_polygon(voronoi, mds_coords):
    d = {}
    for region in voronoi.regions:
        if len(region) == 0:
            continue
        polygon = [voronoi.vertices[i] for i in region]
        centroid = np.mean(polygon, axis=0)
        i = np.argmin(np.linalg.norm(mds_coords - centroid, axis=1))
        d[i] = polygon
    return d

def codevector_index_to_polygon(voronoi, mds_coords):
    d = {}
    for i in range(len(mds_coords)):
        region_index = voronoi.point_region[i]
        region = voronoi.regions[region_index]
        polygon = [voronoi.vertices[i] for i in region]
        d[i] = polygon
    return d
            


def codebook_to_voronoi_set(codebook):
    vset, mdset = [], []
    cb1, cb2 = codebook[:320], codebook[320:]
    for cb in [cb1, cb2, codebook]:
        v, mds = codebook_to_voronoi(cb)
        vset.append(v)
        mdset.append(mds)
    return vset, mdset

def plot_voronoi(voronoi = None, mds_coords = None, 
    codevector_index_to_color = None, codebook = None, phoneme = 't',
    title = 'Voronoi Diagram'):
    if voronoi is None:
        if codebook is None:
            raise ValueError("Either voronoi or codebook must be provided.")
            voronoi, mds_coords = codebook_to_voronoi(codebook)
    if codevector_index_to_color is None:
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
        matrix, cmap, norm = compute_matrix(d=d, phoneme=phoneme, limit=1000) 
        codevector_index_to_color = matrix[0]  
    x_min, x_max, y_min, y_max = xy_points_to_min_max(mds_coords)
    voronoi_dict = codevector_index_to_polygon(voronoi, mds_coords)
    fig, ax = plt.subplots(figsize=(12, 10))
    voronoi_plot_2d(voronoi, ax=ax, show_vertices=False, line_colors='black', 
        line_width=1.5, point_size=0)
    for i in range(len(mds_coords)):
        polygon = voronoi_dict[i]
        plt.fill(*zip(*polygon), color=codevector_index_to_color[i])
    plt.title(title)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.show()



def plot_voronoi_steps(steps, voronoi_step_dict = None, phoneme = 't',
    d = None): 
    if d is None:
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
    if voronoi_step_dict is None:
        voronoi_step_dict = step_to_voronoi_dict(steps)
    output = {}
    for step in steps:
        matrix, cmap, norm = compute_matrix(d=d, phoneme=phoneme, n_rows = 1,
        n_cols = 640, steps = [step], alpha = 0.05, limit = 1000,)
        voronoi, mds_coords = voronoi_step_dict[step]
        title = f"Voronoi Diagram for step {step}, phoneme {phoneme}"
        plot_voronoi(voronoi=voronoi, mds_coords=mds_coords, 
            codevector_index_to_color=matrix[0],
            phoneme=phoneme, title=title)
        output[step] = matrix[0]
    return output
    


