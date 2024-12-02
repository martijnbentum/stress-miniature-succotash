import json
import numpy as np
from pathlib import Path
import pickle
from progressbar import progressbar
from sklearn.metrics import matthews_corrcoef, accuracy_score
from sklearn.metrics import classification_report
from utils import stats

class Results:
    def __init__(self, directory = '../results'):
        self.directory = Path(directory)
        self._set_info()

    def _set_info(self):
        if not self.directory.exists():
            em = f'Directory {self.directory} does not exist'
            raise ValueError(em)
        self.fn = list(self.directory.glob('*.pickle'))
        self.results = []
        for f in progressbar(self.fn):
            if 'mccs' in str(f): continue
            self.results.append(Result(result_filename = f, verbose = False))

    def select_results(self, language_name,  layer, result_type = 'stress',
        section = 'vowel', name = '', n = ''):
        return [r for r in self.results if language_name==r.language_name and
            r.result_type == result_type and
            r.layer == layer and r.section == section and r.name == name and
            r.n == n]

    @property
    def languages(self):
        if not hasattr(self, '_languages'):
            self._languages=list(set([r.language_name for r in self.results]))
        return self._languages

    @property
    def result_types(self):
        if hasattr(self, '_result_types'):
            return self._result_types
        self._result_types=list(set([r.result_type for r in self.results]))
        return self._result_types

    @property
    def layers(self):
        if not hasattr(self, '_layers'):
            temp = list(set([r.layer for r in self.results]))
            self._layers = []
            if 'codevector' in temp:
                self._layers.append('codevector') 
                temp.remove('codevector')
            if 'cnn' in temp:
                self._layers.append('cnn')
                temp.remove('cnn')
            self._layers = self._layers + temp
        return self._layers

    @property
    def sections(self):
        if not hasattr(self, '_sections'):
            self._sections = list(set([r.section for r in self.results]))
        return self._sections

    @property
    def names(self):
        if not hasattr(self, '_names'):
            self._names = list(set([r.name for r in self.results]))
        return self._names

    @property
    def random_state_sets(self):
        if hasattr(self, '_random_state_sets'): return self._random_state_sets
        self._random_state_sets = {}
        for result in self.results:
            if result.identifier not in self._random_state_sets:
                self._random_state_sets[result.identifier] = [result]
            else:
                self._random_state_sets[result.identifier].append(result)
        return self._random_state_sets

        


class Result:
    def __init__(self, y_test = None, hyp = None, result_filename = '',
        result_dict = {}, dataset_dict = {}, verbose = True, 
        result_type = 'stress', random_state = 1,dataset_filename = '',
        classifier_filename = '', **kwargs):
        self.result_filename = result_filename
        self.path = Path(result_filename)
        self.y_test = y_test
        self.hyp = hyp
        self.result_dict = result_dict
        self.verbose = verbose
        self.result_type = result_type
        self.random_state = random_state
        self.dataset_filename = dataset_filename
        self.classifier_filename = classifier_filename
        if not y_test is None and not hyp is None: self._set_metrics()
        elif self.path.exists(): self._load_result()
        elif result_dict: self._set_result_from_dict()
        else:
            em = f'No result provided and no file found at {result_filename}'
            raise ValueError(em)
        self._handle_info(dataset_dict, kwargs)
        self._set_filename()
        if self.name:
            self.identifier = f'{self.language_name}_{self.layer}_{self.name}'
        else:
            self.identifier = f'{self.language_name}_{self.layer}'
        if not self.result_dict: self.to_dict()

    def __repr__(self):
        return self.info_str 

    def __str__(self):
        m = f'result {self.result_filename}\n'
        m += f'language_name: {self.language_name}\n'
        m += f'result_type: {self.result_type}\n'
        m += f'section: {self.section}\n'
        m += f'layer: {self.layer}\n'
        m += f'accuracy: {self.accuracy}\n'
        if not self.categories is None:
            m += f'chance accuracy: {self.chance_accuracy}\n'
            m += f'categories: {self.categories}\n'
        m += f'mcc: {self.mcc}\n'
        m += f'random_state: {self.random_state}\n'
        m += f'classifier_filename: {self.classifier_filename}\n'
        m += f'dataset_filename: {self.dataset_filename}\n'
        return m


    def _set_metrics(self):
        if self.verbose: print('computing metrics')
        self.accuracy = accuracy_score(self.y_test, self.hyp)
        self.mcc = matthews_corrcoef(self.y_test, self.hyp)
        self.report = classification_report(self.y_test, self.hyp)

    def _handle_info(self, dataset_dict, kwargs):
        keys = ['language_name', 'layer', 'section', 'name', 'n']
        for key in keys:
            if hasattr(self, key): continue
            if dataset_dict:
                if key in dataset_dict: setattr(self, key, dataset_dict[key])
            if kwargs:
                if key in kwargs: setattr(self, key, kwargs[key])
        not_handled = [k for k in kwargs if not hasattr(self, k)]
        if not_handled:
            print(f'Not handled in kwargs: {not_handled}')
        missing_info = [k for k in keys if not hasattr(self, k)]
        if missing_info:
            print(f'Missing info: {missing_info}')
            if self.verbose: print('setting info to None')
            for key in missing_info:
                setattr(self, key, None)

    def _load_result(self):
        if self.verbose: print('loading result from file')
        with open(self.result_filename, 'rb') as f:
            d = pickle.load(f)
        self.result_dict = d
        for key in d.keys():
            setattr(self, key, d[key])

    def to_dict(self):
        if self.result_dict: return self.result_dict
        keys = ['language_name', 'result_type', 'layer', 'section', 'accuracy',
            'mcc', 'report', 'name', 'n', 'random_state', 'dataset_filename',
            'classifier_filename', 'hyp', 'y_test']
        self.result_dict = {}
        for key in keys:
            if hasattr(self, key):
                self.result_dict[key] = getattr(self, key)
        return self.result_dict
        
    def _set_filename(self):
        if not self.result_filename:
            f = make_result_filename(self.language_name, self.result_type,
                self.layer, self.section, self.name, self.n, self.random_state)
            self.result_filename = f
            self.path = Path(f)
        return self.result_filename

    def save(self, overwrite = False):
        if self.path.exists() and not overwrite:
            m = f'File {self.result_filename} exists. Use overwrite = True'
            m += 'doing nothing'
            print(m)
            return
        with open(self.result_filename, 'wb') as f:
            pickle.dump(self.result_dict, f)

    @property
    def info_str(self):
        info = f'{self.language_name} {self.result_type} {self.layer}'
        info += f' {self.section} {self.name} {self.n} {self.random_state}'
        info += ' mcc: ' + str(round(self.mcc,3)) 
        return info

    @property
    def info(self):
        names = 'language_name,result_type,layer,section,name,n,random_state'
        output = []
        for name in names.split(','):
             output.append(getattr(self,name))
        return output

    @property
    def categories(self):
        if self.y_test is None: return None
        return np.unique(self.y_test)

    @property
    def chance_accuracy(self):
        if self.y_test is None: return None
        return 1/len(self.categories)

def to_mccs(results_list):
    return [r.mcc for r in results_list]

def _to_mcc_dict(mccs,language_name, classifier_name, mcc_dict = {}):
    if len(mccs) == 0: 
        raise ValueError('No mccs provided')
    if not language_name in mcc_dict: mcc_dict[language_name] = {}
    if not classifier_name in mcc_dict[language_name]:
        mcc_dict[language_name][classifier_name] = {}
    mcc_dict[language_name][classifier_name]['mccs'] = mccs
    mean, sem, ci = stats.compute_mean_sem_ci(mccs)
    mcc_dict[language_name][classifier_name]['mean'] = mean
    mcc_dict[language_name][classifier_name]['sem'] = sem
    mcc_dict[language_name][classifier_name]['ci'] = ci
    return mcc_dict


def results_filename_to_info(filename):
    f = str(filename)
    f = f.split('/')[-1].split('.')[0]
    language_name,result_type,layer,section,name,n,random_state = f.split('_')
    return language_name,result_type,layer,section,name,n,random_state


def make_result_filename(language_name, result_type, layer, section, name, n,
    random_state):
    f = f'../results/{language_name}_{result_type}_{layer}_'
    f += f'{section}_{name}_{n}_{random_state}.pickle'
    return f

def save_results(y_test, hyp, language_name, data_type, layer, section, 
    name, n, rs, dataset_filename, classifier_filename, overwrite = False):
    result = Result(y_test = y_test, hyp = hyp, 
        language_name = language_name,
        layer = layer, section = section, name = name, n = n, 
        random_state = rs, result_type = data_type,
        dataset_filename = dataset_filename, 
        classifier_filename = classifier_filename)
    print(result)
    result.save(overwrite = overwrite)
    return result



