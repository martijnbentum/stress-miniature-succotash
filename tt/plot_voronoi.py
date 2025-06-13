import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

def plot_voronoi(voronoi, mds_coords, step = None):
    x_min, x_max, y_min, y_max = xy_points_to_min_max(mds_coords)
    voronoi_dict = codevector_index_to_polygon(voronoi, mds_coords)
    fig, ax = plt.subplots(figsize=(12, 10))
    voronoi_plot_2d(voronoi, ax=ax, show_vertices=False, line_colors='black', 
        line_width=1.5, point_size=0)
    for i in range(len(mds_coords)):
        polygon = voronoi_dict[i]
        plt.fill(*zip(*polygon), color='white')
    title ='Voronoi' if step is None else f'Voronoi - Codebook Step {step}'
    plt.title(title)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.show()
    return fig, ax, voronoi_dict

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
