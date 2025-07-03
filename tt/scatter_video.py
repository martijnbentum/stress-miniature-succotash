import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from sklearn.manifold import TSNE
from tt import select_materials
from tt import compute_codevectors as cc

def make_scatter_animation(data, c = None, phones = None, cmap = 'viridis', 
    interval = 500,frame_names = [], alpha = 1):
    """
    Create a scatter plot animation from the given data.

    Parameters:
    - data: A 3D numpy array where each row is a point (frames, x, y).
    - c: Optional. A 1D array of values to color the points len(x) values.
    - cmap: Colormap to use for coloring the points.
    - interval: Time between frames in milliseconds.

    Returns:
    - FuncAnimation object.
    """

    def get_x_y(frame):
        x = data[frame,:,0]
        y = data[frame,:,1]
        return x , y

    x, y = get_x_y(0)
    fig, ax = plt.subplots()
    bounds = np.arange(0, len(phones) + 1)
    norm = BoundaryNorm(bounds, ncolors=len(phones), clip=True)
    sc = ax.scatter(x, y, c=c, cmap=cmap, alpha = alpha)#, norm=norm,)
    cbar=plt.colorbar(sc, ax=ax, label='phones', ticks=np.arange(len(phones)))
    cbar.ax.set_yticklabels(phones)
    frame_index = 0
    n_frames = data.shape[0]
    playing = True

    ax_play = plt.axes([0.4, 0.05, 0.1, 0.075])
    ax_back = plt.axes([0.25, 0.05, 0.1, 0.075])
    ax_fwd = plt.axes([0.55, 0.05, 0.1, 0.075])

    btn_play = Button(ax_play, 'Play/Pause')
    btn_back = Button(ax_back, 'Back')
    btn_fwd = Button(ax_fwd, 'Forward')

    def toggle_play(event):
        nonlocal playing
        playing = not playing

    def step_forward(event):
        nonlocal frame_index, n_frames, playing
        playing = False
        frame_index = min(frame_index + 1, n_frames - 1)
        update(frame_index)
        fig.canvas.draw_idle()

    def step_back(event):
        nonlocal frame_index, playing
        playing = False
        frame_index = max(frame_index - 1, 0)
        update(frame_index)
        fig.canvas.draw_idle()

    btn_play.on_clicked(toggle_play)
    btn_back.on_clicked(step_back)
    btn_fwd.on_clicked(step_forward)

    def set_limits(x, y):
        print('Setting limits', np.min(x), np.max(x), np.min(y), np.max(y))
        xmin, xmax, ymin, ymax =  np.min(x), np.max(x), np.min(y), np.max(y)
        ax.set_xlim(xmin *.9, xmax * 1.1)
        ax.set_ylim(xmin *.9, ymax * 1.1)

    def init():
        return sc,

    def update(frame):
        x, y = get_x_y(frame)
        if frame_names: frame_name = frame_names[frame]
        else: frame_name = frame
        ax.set_title(f'step {frame_name}')
        sc.set_offsets(data[frame])
        set_limits(x, y)
        return sc,

    def animate(_):
        nonlocal frame_index, playing
        if playing:
            frame_index = (frame_index + 1) % len(data)
            return update(frame_index)

    ani = FuncAnimation(fig, animate, frames=len(data), init_func=init, 
        blit=False, interval=interval)
    plt.show()
    return ani

def get_cb_from_step(step, cb_index = 0):
    cb = cc. language_step_to_codebook('nl', step, load_saved_codebook = True)
    if cb_index == 0:
        return cb[:320,:]
    if cb_index == 1:
        return cb[320:,:]
    elif cb_index is None:
        print('warning returning both codebooks in one matrix')
        return cb
    raise ValueError(f'Unknown cb_index {cb_index}')

    

def get_phone_cb_indices(phone, step, d = None, cb_index = 0):
    if d is None: 
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
    cb_cutoff = 320
    indices = d[phone][f'nl-{step}-cgn']
    output = []
    for line in indices:
        for item in line:
            if type(item) == list: output.append(item[0])
            if cb_index == 0:
                if type(item) == int and item < 320: output.append(item)
            if cb_index == 1:
                if type(item) == int and item > 320: output.append(item)
    return output
    
def select_codevectors(cb, indices):
    return np.array([cb[index,:] for index in indices])
    
def make_c(n_categories, n_tokens):
    output = []
    for i in range(n_categories):
        output.extend([i] * n_tokens)
    return output
        

def make_data(steps, phones, function = None, cb_index = 0, limit = 100, 
    d = None):
    if function is None:
        tsne = TSNE(n_components=2, random_state=42, perplexity=30, 
            init='pca')
        function = tsne.fit_transform
    if d is None:
        d = select_materials.collect_phoneme_codevector_indices(limit = 1000)
    data = np.zeros((len(steps), limit * len(phones), 2))
    for i, step in enumerate(steps):
        cb = get_cb_from_step(step, cb_index)
        phones_cv = []
        for phone in phones:
            phone_cv_indices = get_phone_cb_indices(phone, step, d)
            phone_cv = select_codevectors(cb, phone_cv_indices[:limit])
            phones_cv.append(phone_cv)
        phones_cv = np.concatenate(phones_cv, axis=0)
        data[i] = function(phones_cv)
    return data
        


    
