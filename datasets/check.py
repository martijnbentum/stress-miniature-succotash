import glob
import numpy
import pickle

def check_xy_datasets(language_name):
    fn = glob.glob('../dataset/xy_dataset-stress_language-dutch*')
    counts, stressed = [], []
    for f in fn:
        d = pickle.load(open(f,'rb'))
        n = len(d['X'])
        n_stressed = sum(d['y'])
        print('loading', f)
        print('n:',n, 'n_stressed:',n_stressed)
        counts.append(n)
        stressed.append(n_stressed)
    print('max difference:', max(counts) - min(counts))
    print('max difference stressed:', max(stressed) - min(stressed)


