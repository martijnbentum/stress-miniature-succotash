from collections import Counter
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches
from progressbar import progressbar
from scipy.spatial.distance import jensenshannon
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import fowlkes_mallows_score
from sklearn.metrics import normalized_mutual_info_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import silhouette_score
from sklearn.metrics import matthews_corrcoef as mcc
from scipy.optimize import linear_sum_assignment
from sklearn.preprocessing import LabelEncoder

base = '/vol/mlusers/mbentum/st_phonetics/'
codebook_dir = base + 'codebooks/'

def plot_dendrogram(js_distances):
    # Extract unique phones
    phones = sorted(set(i for i, j in js_distances.keys()))

    # Create a condensed distance matrix (needed for clustering)
    size = len(phones)
    distance_matrix = np.zeros((size, size))
    for (p1, p2), dist in js_distances.items():
        i, j = phones.index(p1), phones.index(p2)
        distance_matrix[i, j] = dist
        distance_matrix[j, i] = dist  # Ensure symmetry

    # Convert to condensed form (1D array) for scipy linkage
    condensed_distances = squareform(distance_matrix)

    # Perform hierarchical clustering using Ward's method
    linkage_matrix = linkage(condensed_distances, method="ward")

    # Plot the dendrogram
    plt.figure(figsize=(6, 5))
    dendrogram(linkage_matrix, labels=phones, leaf_rotation=45, leaf_font_size=10)
    plt.title("Dendrogram of Phones (JS Distance)")
    plt.ylabel("Cluster Distance")
    plt.show()

def compute_adjusted_rand_score(count_dict, language = 'nl'):
    fine_labels = list(phone_to_fine_phonetic_class_dict().values())
    broad_labels = list(phone_to_broad_phonetic_class_dict().values())
    jsd = count_dict_to_js_distance_dict(count_dict)
    matrix = jsd_distance_dict_to_matrix(jsd)
    bc = AgglomerativeClustering(n_clusters=2, metric='precomputed', 
        linkage='average')
    fc = AgglomerativeClustering(n_clusters=9, metric='precomputed',
        linkage='average')
    hyp_broad = bc.fit_predict(matrix)
    mapped_broad = map_cluster_labels(broad_labels, hyp_broad)
    hyp_fine = fc.fit_predict(matrix)
    mapped_fine = map_cluster_labels(fine_labels, hyp_fine)
    return {'fine_ars':adjusted_rand_score(mapped_fine, hyp_fine), 
        'broad_ars':adjusted_rand_score(mapped_broad, hyp_broad),
        'fine_fmi':fowlkes_mallows_score(mapped_fine, hyp_fine),
        'broad_fmi':fowlkes_mallows_score(mapped_broad, hyp_broad),
        'fine_nmi':normalized_mutual_info_score(mapped_fine, hyp_fine),
        'broad_nmi':normalized_mutual_info_score(mapped_broad, hyp_broad),
        'fine_cm':confusion_matrix(mapped_fine, hyp_fine),
        'broad_cm':confusion_matrix(mapped_broad, hyp_broad),
        'fine_silhouette':silhouette_score(matrix, hyp_fine),
        'broad_silhouette':silhouette_score(matrix, hyp_broad),
        'fine_mcc':mcc(mapped_fine, hyp_fine),
        'broad_mcc':mcc(mapped_broad, hyp_broad),
        'fine_hyp':hyp_fine,
        'broad_hyp':hyp_broad,
        'fine_mapped':mapped_fine,
        'broad_mapped':mapped_broad,
        'fine_labels':fine_labels,
        'broad_labels':broad_labels
        }

    


def phone_to_finest_phonetic_class_dict(md = None):
    return phone_to_phonetic_class_dict(md, 'fine')

def phone_to_broad_phonetic_class_dict(md = None):
    return phone_to_phonetic_class_dict(md, 'broad')

def phone_to_fine_phonetic_class_dict(md = None):
    if not md:
        md = load_metadata()
    output = {}
    for line in md:
        phone = line['phone']
        fine_phonetic_class = line['fine_category']
        output[phone] = fine_phonetic_class
    return output

def load_codebook_file(filename):
    with open(filename, "r") as f:
        return json.load(f)

def _codebook_filename_to_step(filename):
    return int(filename.split('_')[-1].split('.')[0])

def _codebook_filename_to_language(filename):
    return filename.split('_')[-2]

def load_metadata(filename = base + 'mls-1sp-phone-eval-subset.tsv'):
    with open(filename, "r") as fin:
        t = fin.read().split('\n')
    t = [x.split('\t') for x in t]
    header = t[0]
    data = t[1:]
    output = []
    for line in data:
        if len(line) != len(header):
            continue
        d = dict(zip(header, line))
        output.append(d)
    return output

def combine_ci_and_metadata_to_phone_ci_dict(ci, metadata):
    output = {}
    for i in range(len(metadata)):
        line = metadata[i]
        phone = line['phone']
        if phone not in output.keys(): output[phone] = []
        codebook_indices = ci[i]
        output[phone].extend(codebook_indices)
    for phone, ci in output.items():
        output[phone] = Counter(ci)
    
    return output

def load_codebook_files(language = 'nl'):
    pattern = codebook_dir + '*' +language + '*.json'
    fn = glob.glob(pattern)
    fn.sort(key=_codebook_filename_to_step)
    md = load_metadata()
    output = []
    for f in fn:
        step = _codebook_filename_to_step(f)
        language = _codebook_filename_to_language(f)
        ci = load_codebook_file(f)
        count_dict = combine_ci_and_metadata_to_phone_ci_dict(ci, md)
        line = {'ci':ci, 
            'count_dict':count_dict,
            'language':language,
            'step':step,
            'filename':f}
        output.append(line)
    return output
    
    



def js_distance(counts1, counts2):
    """Compute Jensen-Shannon distance from two count dictionaries."""
    
    # Convert counts to probability distributions
    total1, total2 = sum(counts1.values()), sum(counts2.values())
    keys = set(counts1.keys()).union(set(counts2.keys()))  # All unique keys
    
    # Normalize to probabilities
    p = np.array([counts1.get(k, 0) / total1 for k in keys])
    q = np.array([counts2.get(k, 0) / total2 for k in keys])

    # Compute Jensen-Shannon distance
    return jensenshannon(p, q, base=2)  # base=2 gives distance in bits

def count_dict_to_js_distance_dict(count_dict):
    output = {}
    for phone1, counts1 in count_dict.items():
        for phone2, counts2 in count_dict.items():
            # if phone1 == phone2: continue
            # if (phone2, phone1) in output.keys(): continue
            output[(phone1, phone2)] = js_distance(counts1, counts2)
    return output

def jsd_distance_dict_to_matrix(jsd_distance_dict):
    phones = list(set([x[0] for x in jsd_distance_dict.keys()]))
    print('phones:', len(phones), phones)
    matrix = np.zeros((len(phones), len(phones)))
    for i in range(len(phones)):
        for j in range(len(phones)):
            if i == j: continue
            phone1, phone2 = phones[i], phones[j]
            matrix[i, j] = jsd_distance_dict[(phone1, phone2)]
    return matrix

def phone_to_phonetic_class_dict(md = None,phonetic_class = 'fine'):
    if phonetic_class not in ['fine', 'broad']:
        raise ValueError('phonetic_class must be either "fine" or "broad"')
    phonetic_class = phonetic_class + '_category'
    if not md:
        md = load_metadata()
    output = {}
    for line in md:
        phone = line['phone']
        if phone in output.keys(): continue
        label = line[phonetic_class]
        output[phone] = label
    return output

def map_cluster_labels(true_labels, pred_labels):
    """
    Maps predicted cluster labels to ground truth labels for best matching.
    
    Args:
        true_labels (array-like): Ground truth labels.
        pred_labels (array-like): Predicted cluster labels.

    Returns:
        mapped_pred_labels (np.array): Predicted labels mapped to best-matching ground truth labels.
        label_mapping (dict): Mapping of predicted labels to true labels.
        ari (float): Adjusted Rand Index after mapping.
    """
    if type(true_labels[0]) == str:
        labels = list(set(true_labels))
        true_labels = np.array([labels.index(label) for label in true_labels])
        
    # Convert labels to numpy arrays
    true_labels = np.array(true_labels)
    pred_labels = np.array(pred_labels)

    # Compute confusion matrix
    conf_matrix = confusion_matrix(true_labels, pred_labels)

    # Find best mapping using Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(-conf_matrix)  # Maximize assignment

    # Create mapping dictionary
    label_mapping = {pred: true for true, pred in zip(row_ind, col_ind)}

    # Apply mapping to predicted labels
    mapped_true_labels = np.array([label_mapping[label] for label in true_labels])
    return mapped_true_labels

'''
def cbi_to_counts(item):
    ci = item.codebook_indices()
    unique, counts = np.unique(ci, return_counts=True)
    return Counter(dict(zip(unique, counts)))

def phones_to_cbi_counts(phones):
    o = {}
    for phone in progressbar(phones):
        if phone.ipa not in o.keys():
            o[phone.ipa] = cbi_to_counts(phone)
        else:
            o[phone.ipa] += cbi_to_counts(phone)
    return o
'''
