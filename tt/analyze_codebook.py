import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from sklearn.manifold import MDS
from sklearn.metrics import pairwise_distances


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

def compute_point_stress(codebook):
    mds_coords = compute_mds(codebook)
    distance_matrix = compute_distance_matrix(codebook)
    diff = (distance_matrix - pairwise_distances(mds_coords)) **2
    point_stress = np.sum(diff, axis = 1)
    return point_stress

def kruskal_stress(codebook):
    mds_coords = compute_mds(codebook)
    distance_matrix = compute_distance_matrix(codebook)
    diff = (distance_matrix - pairwise_distances(mds_coords)) **2
    kruskal_stress = np.sum(diff) / np.sum(distance_matrix ** 2)
    return kruskal_stress ** .5
