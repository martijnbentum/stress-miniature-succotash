'''code from ankita pasad refactored with gpt5'''
import os
import numpy as np
import scipy
from scipy.signal import find_peaks


# ------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------

def load_alignment_data(fnames, sentence_ids, data_dir, alignment_dir, 
    sentence_frames):
    """Fetch word/phone alignments for the corpus."""
    return get_word_alignment(fnames, sentence_ids, data_dir, alignment_dir, 
        sentence_frames)


def list_npy_files(rep_dir):
    """Return all .npy files in a directory."""
    return [f for f in os.listdir(rep_dir) if f.endswith(".npy")]


def load_layer_vectors(rep_dir, layer, sentence_frames):
    """Load the representation matrix for a specific layer."""
    for f in list_npy_files(rep_dir):
        if int(f.split('.')[0].split('_')[1]) == layer:
            path = os.path.join(rep_dir, f)
            vecs = np.load(path)
            assert vecs.shape[0] == sum(sentence_frames)
            return vecs
    raise ValueError(f"No matching npy file found for layer {layer}")


def zscore_vecs(vecs):
    """Z-score normalize vectors along the feature dimension."""
    return scipy.stats.zscore(vecs, axis=0)


# ------------------------------------------------------------
# Distance computation
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Peak detection
# ------------------------------------------------------------

def detect_peaks(vecs_smooth, prominence, window_size):
    """Detect peaks with scipy and adjust index offset."""
    peaks, info = find_peaks(vecs_smooth, prominence=prominence)
    if info["prominences"].size == 0:
        return np.array([])

    # Sort by prominence
    prominences, peaks = zip(*sorted(zip(info["prominences"], peaks), 
        reverse=True))
    peaks = np.array(peaks) + window_size // 2
    return np.sort(peaks)


# ------------------------------------------------------------
# Boundary extraction
# ------------------------------------------------------------

def extract_sentence_boundaries(alignment):
    """Extract sorted unique word boundary times."""
    return sorted(set(time for unit in alignment for time in unit[2:4]))


# ------------------------------------------------------------
# Sentence-level processing
# ------------------------------------------------------------

def process_sentence(i, sentence_frames, sentence_ids, alignments, vecs_norm, 
    dist, window_size, prominence):
    """Process a single sentence: compute boundaries and peak locations."""
    word_alignment, _ = alignments[i]
    boundaries = extract_sentence_boundaries(word_alignment)

    start = sum(sentence_frames[:i])
    end = sum(sentence_frames[:i+1])
    vecs_selected = vecs_norm[start:end]

    vecs_diff = compute_distance(vecs_selected, dist)
    vecs_smooth = average_pooling(vecs_diff, window_size)

    peaks = detect_peaks(vecs_smooth, prominence, window_size)

    return boundaries, peaks


# ------------------------------------------------------------
# Hyperparameter search loop
# ------------------------------------------------------------

def search_best_parameters(
    layers,
    alignments,
    sentence_frames,
    sentence_ids,
    rep_dir,
    prominence_values,
    dist_metrics,
    window_sizes,
    stride_sec,
    tolerance,
):
    best_results = {}

    for layer in layers:
        vecs = load_layer_vectors(rep_dir, layer, sentence_frames)
        layer_best = {
            "f1": 0,
            "distance": None,
            "window": None,
            "prominence": None,
            "precision": None,
            "recall": None,
        }

        for prominence in prominence_values:
            for dist in dist_metrics:
                for window_size in window_sizes:

                    vecs_norm = zscore_vecs(vecs)

                    all_boundaries = []
                    all_peaks = []

                    for i in range(len(sentence_ids)):
                        boundaries, peaks = process_sentence(
                            i,
                            sentence_frames,
                            sentence_ids,
                            alignments,
                            vecs_norm,
                            dist,
                            window_size,
                            prominence,
                        )
                        all_boundaries.append(boundaries)
                        all_peaks.append(peaks)

                    precision, recall, f1 = f1_score(
                        all_boundaries, all_peaks, stride_sec, tolerance
                    )

                    if f1 > layer_best["f1"]:
                        layer_best.update({
                            "f1": f1,
                            "distance": dist,
                            "window": window_size,
                            "prominence": prominence,
                            "precision": precision,
                            "recall": recall,
                        })

        best_results[layer] = {
            "distance metric": layer_best["distance"],
            "window size": layer_best["window"],
            "prominence": layer_best["prominence"],
            "f1": layer_best["f1"],
        }

    return best_results

