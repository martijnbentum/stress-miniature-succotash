import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors, cm
from matplotlib.colorbar import ColorbarBase
from sklearn.metrics.pairwise import cosine_distances
from sklearn.manifold import MDS
from .step_list import steps
from .general import flatten_list
from . import select_materials
from scipy.spatial import Voronoi, voronoi_plot_2d
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

def _grid_indices_to_index_mapper(grid_indices, n_rows = 32, n_cols = 20):
    index_mapper = {}
    for i in range(n_rows):
        for j in range(n_cols):
            index_mapper[ grid_indices[i, j] ] = (i, j)
    return index_mapper

def compute_distance_matrix(codebook):
    distance_matrix = cosine_distances(codebook)
    return distance_matrix

def compute_mds(codebook, n_components=2, dissimilarity='precomputed', 
    random_state=42):
    distance_matrix = compute_distance_matrix(codebook)
    mds = MDS(n_components=n_components, dissimilarity=dissimilarity, 
    random_state=random_state)
    mds_coords = mds.fit_transform(distance_matrix)
    return mds_coords

def compute_index_mapper(codebook, n_rows = 32, n_cols = 20,):
    mds_coords = compute_mds(codebook)
    sorted_indices = np.lexsort(mds_coords[:,0], mds_coords[:,1])
    grid_indices = np.array(sorted_indices).reshape(n_rows, n_cols)
    index_mapper = _grid_indices_to_index_mapper(grid_indices, n_rows, n_cols)
    return index_mapper
    

def compute_matrix(d = None, phoneme = 't', limit = 100, alpha = 0.05, 
    cmap_name='viridis', steps = steps, n_rows = 32, n_cols = 20,
    codebook = None, do_load_codebook = None, index_mapper = None, 
    step = None,):
    if d is None:
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
    if codebook is not None or do_load_codebook: 
        if codebook is None and index_mapper is None: 
            codebook = cc.language_step_to_codebook('nl',step)
        if index_mapper is None:
            index_mapper = compute_index_mapper(codebook)
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

def codevector_index_to_polygon(voronoi, mds_coords):
    d = {}
    for region in voronoi.regions:
        if len(region) == 0:
            continue
        polygon = [voronoi.vertices[i] for i in region]
        centroid = np.mean(polygon, axis=0)
        i = np.argmin(np.linalg.norm(mds_coords - centroid, axis=1))
        
        d[i] = polygon
    return d
            

def codebook_to_voronoi(codebook):
    mds_coords = compute_mds(codebook)
    voronoi = Voronoi(mds_coords)
    voronoi_dict = codevector_index_to_polygon(voronoi, mds_coords)
    return voronoi, voronoi_dict



