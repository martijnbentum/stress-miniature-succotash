import numpy as np

def compute_mean_sem_ci(data, ci_value = 2.576):
    mean = np.mean(data)
    sem = np.std(data) / np.sqrt(len(data))
    ci = sem * ci_value
    return mean, sem, ci
