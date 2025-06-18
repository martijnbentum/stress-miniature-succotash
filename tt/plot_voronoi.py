import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.spatial import Voronoi, voronoi_plot_2d

def plot_voronoi(voronoi, mds_coords, step = None, ax = None,
    set_polygon_to_white=True, title=None, line_width = 1, 
        title_color = 'black'):
    x_min, x_max, y_min, y_max = xy_points_to_min_max(mds_coords)
    voronoi_dict = codevector_index_to_polygon(voronoi, mds_coords)
    if not ax:
        fig, ax = plt.subplots(figsize=(12, 10))
    voronoi_plot_2d(voronoi, ax=ax, show_vertices=False, line_colors='black', 
        line_width=line_width, point_size=0)
    if set_polygon_to_white:
        for i in range(len(mds_coords)):
            polygon = voronoi_dict[i]
            ax.fill(*zip(*polygon), color='white')
    if title is None:
        title ='Voronoi' if step is None else f'Voronoi - Codebook Step {step}'
    ax.set_title(title, color = title_color)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    plt.show()
    return ax, voronoi_dict

def plot_voronoi_set(voronoi_set, mds_coords_set, step=None):
    if len(voronoi_set) != 4 or len(mds_coords_set) != 4:
        voronoi_set.append(voronoi_set[-1])
        mds_coords_set.append(mds_coords_set[-1])
    if len(voronoi_set) !=  len(mds_coords_set):
        raise ValueError('voronoi_set and mds_coords_set must have the same length')
    plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(2,2)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[1, 0])
    ax4 = plt.subplot(gs[1, 1])
    axes = [ax1, ax2, ax3, ax4]
    titles = ['codebook 1', 'codebook 2', 'both codebooks', 'both codebooks ']
    for v, mds, ax, title in zip(voronoi_set, mds_coords_set, axes, titles):
        if title == 'codebook 1': title_color = 'blue'
        elif title == 'codebook 2': title_color = 'red'
        else: title_color = 'black'
        plot_voronoi(v, mds, step=step, ax=ax, title = title, 
            set_polygon_to_white = False, title_color = title_color)
        if title == 'both codebooks':
            voronoi_dict = codevector_index_to_polygon(v, mds)
            for i in range(len(mds)):
                if i < 320: color = 'blue'
                else: color = 'red'
                polygon = voronoi_dict[i]
                ax.fill(*zip(*polygon), color = color)
    plt.suptitle(f'Voronoi Diagrams for Codebooks at Step {step}')
    return axes

def color_polygon(codevector_index, voronoi, mds, ax, color = 'black', alpha = 1):
    voronoi_dict = codevector_index_to_polygon(voronoi, mds)
    if len(voronoi_dict) == 320 and 640 > codevector_index > 319 :
        codevector_index -= 320
    ax.fill(*zip(*voronoi_dict[codevector_index]), color=color, alpha=alpha)

def color_polygon_set(codevector_index, voronoi_set, mds_coords_set, axes, 
    color = 'black', alpha = 1):
    print('coloring polygon for codevector index:', codevector_index)
    if codevector_index < 320: 
        ax = axes[0]
        v, mds = voronoi_set[0], mds_coords_set[0]
        color_polygon(codevector_index, v, mds, ax, color=color, alpha=alpha)
    else: 
        ax = axes[1]
        v, mds = voronoi_set[1], mds_coords_set[1]
        color_polygon(codevector_index, v, mds, ax, color=color, alpha=alpha)
    ax = axes[-1]
    v, mds = voronoi_set[-1], mds_coords_set[-1]
    color_polygon(codevector_index, v, mds, ax, color=color, alpha=alpha)

def color_polygon_couple(codevector_couple, voronoi_set, mds_coords_set, axes,
    color1 = 'blue', color2 = 'red', alpha = 1):
    index1, index2 = codevector_couple
    for index, color in zip([index1, index2], [color1, color2]):
        color_polygon_set(index, voronoi_set, mds_coords_set, axes, 
            color=color, alpha=alpha)

    

def xy_points_to_min_max(xy_points):
    """Convert a list of xy points to min and max values."""
    x_min = min(xy_points[:, 0])
    x_max = max(xy_points[:, 0])
    y_min = min(xy_points[:, 1])
    y_max = max(xy_points[:, 1])
    return x_min, x_max, y_min, y_max

def codevector_index_to_polygon(voronoi, mds_coords):
    d = {}
    for i in range(len(mds_coords)):
        region_index = voronoi.point_region[i]
        region = voronoi.regions[region_index]
        polygon = [voronoi.vertices[i] for i in region]
        d[i] = polygon
    return d
