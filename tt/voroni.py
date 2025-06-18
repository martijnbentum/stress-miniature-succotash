from . import compute_codevectors as cc
from . import analyze_codebook
from scipy.spatial import Voronoi 

def codebook_to_voronoi(codebook):
    mds_coords = analyze_codebook.compute_mds(codebook)
    mds_coords_d = add_distant_dummy_points(mds_coords)
    voronoi = Voronoi(mds_coords_d)
    return voronoi, mds_coords 

def step_to_voronoi(step, codebook = None):
    if codebook is None:
        codebook = cc.language_step_to_codebook('nl', step)
    voronoi, mds_coords = codebook_to_voronoi(codebook)
    return voronoi, mds_coords

def step_to_voronoi_set(step, codebook = None):
    if codebook is None:
        codebook = cc.language_step_to_codebook('nl', step,
            load_saved_codebook = True)
    voronoi_set, mds_coords_set = codebook_to_voronoi_set(codebook)
    return voronoi_set, mds_coords_set

def step_to_voronoi_dict(steps):
    voronoi_dict = {}
    for step in progressbar(steps):
        filename = f'../voronoi/voronoi_nl-{step}.pickle'
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                voronoi, mds_coords = pickle.load(f)
        else:
            voronoi, mds_coords = step_to_voronoi(step)
            with open(filename, 'wb') as f:
                pickle.dump((voronoi, mds_coords), f)
        voronoi_dict[step] = voronoi, mds_coords
    return voronoi_dict

def step_to_voronoi_set_dict(steps):
    voronoi_dict = {}
    for step in progressbar(steps):
        filename = f'../voronoi/voronoi_set_nl-{step}.pickle'
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                voronoi, mds_coords = pickle.load(f)
        else:
            voronoi, mds_coords = step_to_voronoi_set(step)
            with open(filename, 'wb') as f:
                pickle.dump((voronoi, mds_coords), f)
        voronoi_dict[step] = voronoi, mds_coords
    return voronoi_dict
