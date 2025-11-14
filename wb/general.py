import os
import numpy as np
import scipy
from scipy.signal import find_peaks


def process_embedding(frames, layer, window_size = 3, prominence = 0.3,
    distance_type = 'eucli'):
    X = np.array([f.transformer(layer) for f in frames.frames])
    Xz = zscore_vecs(X)
    Xdifference= compute_distance(Xz, distance_type)
    Xsmooth= average_pooling(Xdifference, window_size)
    peaks = detect_peaks(Xsmooth, prominence, window_size)
    return peaks, Xdifference, Xsmooth

def detect_peaks(vecs_smooth, prominence, window_size):
    """Detect peaks with scipy and adjust index offset.
    """
    peaks, info = find_peaks(vecs_smooth, prominence=prominence)
    if info["prominences"].size == 0:
        return np.array([])

    # Sort by prominence
    prominences, peaks = zip(*sorted(zip(info["prominences"], peaks), 
        reverse=True))
    peaks = np.array(peaks) + window_size // 2
    return np.sort(peaks)

def peak_times_from_envelope(env, sample_rate=16_000, 
    min_interval_ms=80, prominence=None):
    distance = int(sample_rate * (min_interval_ms/1000))
    peaks, _ = find_peaks(env, distance=distance, prominence=prominence)
    return peaks / sample_rate

def zscore_vecs(vecs):
    """Z-score normalize vectors along the feature dimension."""
    return scipy.stats.zscore(vecs, axis=0)

def compute_euclidean_diff(vecs):
    """Euclidean frame-to-frame change."""
    return np.linalg.norm(vecs[1:] - vecs[:-1], axis=1)

def compute_cosine_diff(vecs):
    """Cosine frame-to-frame distance."""
    v1, v2 = vecs[1:], vecs[:-1]
    num = np.sum(v1 * v2, axis=1)
    denom = np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1)
    return 1 - num / denom

def compute_distance(vecs, metric):
    """Select distance metric."""
    if metric == "eucli":
        return compute_euclidean_diff(vecs)
    elif metric == "cosine":
        return compute_cosine_diff(vecs)
    else:
        raise ValueError(f"Unknown distance metric: {metric}")

def average_pooling(vecs, n):
    ret = np.cumsum(vecs, axis=0)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def plot_power_spectrum(x, sample_rate=16_000, xlim = (0,100)):
    f, Pxx = welch(x, fs=sample_rate, nperseg=1024)
    plt.figure()
    plt.semilogy(f, Pxx)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD (power/Hz)")
    plt.title("Power Spectral Density (Welch)")
    plt.xlim(xlim)
    plt.show()
