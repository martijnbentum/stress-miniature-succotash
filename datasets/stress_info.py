from utils import locations
from utils import load_hidden_states as lhs
import numpy as np
import pickle
from progressbar import progressbar
import random

class StressInfo:
    def __init__(self, syllables, dataset_name = 'default', 
        model = 'wav2vec2-xls-r-300m'):
        self.syllables= syllables
        self.dataset_name = dataset_name
        self.model = model
        self._set_info()

    def _set_info(self):
        



