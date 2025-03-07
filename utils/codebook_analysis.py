import numpy as np
from collections import Counter
from progressbar import progressbar

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





