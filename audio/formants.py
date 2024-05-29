import json
from utils import locations
import os
from pathlib import Path
from progressbar import progressbar
import random
import string
import sys

def handle_audio(audio):
    formants = Formants(audio)
    words = audio.word_set.all()
    for word in progressbar(words):
        handle_word(word, formants)

def handle_word(word, formants, save = True):
    phonemes = word.phoneme_set.all()
    for phoneme in phonemes:
        handle_phoneme(phoneme, formants, save)

def handle_phoneme(phoneme, formants, save = True):
    f1, f2 = formants.f1_f2(phoneme)
    phoneme._f1 = json.dumps(f1)
    phoneme._f2 = json.dumps(f2)
    if save: phoneme.save()

class Formants:
    '''class to handle formant values for an audio file
    formant values are stored in a table file
    the formant values are computed with Praat
    '''
    def __init__(self, audio):
        self.audio = audio 
        self.table, self.header = load_formants(audio)
        self._make_formant_lines()

    def _make_formant_lines(self):
        self.formant_lines = [Formant_line(x) for x in self.table]

    def interval(self, start, end):
        lines = self.formant_lines
        lines = [x for x in lines if x.time >= start and x.time <= end]
        return lines

    def interval_mean_f1_f2(self, start, end):
        lines = self.interval(start, end)
        f1 = round(sum([x.f1 for x in lines]) / len(lines))
        f2 = round(sum([x.f2 for x in lines]) / len(lines))
        return f1, f2

    def mean_f1_f2(self, item):
        '''return mean f1 and f2 for item, typically a phoneme object
        phoneme object is defined in word.py
        '''
        start, end = item.start_time, item.end_time
        return self.interval_mean_f1_f2(start, end)

    def f1_f2(self, item):
        '''return all f1 and f2 values for item, typically a phoneme object
        phoneme object is defined in word.py
        '''
        start, end = item.start_time, item.end_time
        lines = self.interval(start, end)
        f1 = [round(x.f1) for x in lines]
        f2 = [round(x.f2) for x in lines]
        return f1, f2

            


class Formant_line:
    '''line from formant table with time and formant values'''
    def __init__(self, line):
        self.line = line
        self.time = float(line[0])
        self.nformants = int(line[1])
        self.f1 = float(line[2])
        self.f2 = float(line[4])

    def __repr__(self):
        return 'Time: {}, F1: {}, F2: {})'.format(self.time, self.f1, self.f2)


def load_formants(audio):
    '''load table file with formant values for word
    word is a word object defined in word.py
    '''
    filename = audio_to_formant_filename(audio)
    with open(filename, 'r') as f:
        temp= [x.split('\t') for x in f.read().split('\n') if x]
    header, table = temp[0], temp[1:]
    return table, header


def praat_script_filename():
    name = ''.join(random.sample(string.ascii_lowercase*10,30))
    filename = '../praat/' + name + '.praat'
    return filename

def handle_audio(audio):
    cmd = audio_praat_cmd(audio)
    filename_praat_script = praat_script_filename()
    with open(filename_praat_script, 'w') as fout:
        fout.write(cmd)
    if sys.platform == 'darwin':
        m = '/Applications/Praat.app/Contents/MacOS/Praat'
    else:
        m = 'praat'
    m += ' --run ' + filename_praat_script
    print(m)
    os.system(m)
    os.remove(filename_praat_script)

    

def audio_to_formant_filename(audio):
    formant_directory = locations.formants_dir.resolve()
    name = Path(audio.filename).stem + '.formants'
    filename = formant_directory / name
    return filename

def audio_praat_cmd(audio):
    formant_filename = audio_to_formant_filename(audio)
    audio_filename = Path(audio.filename).resolve()
    name = audio_filename.stem
    cmd = []
    cmd.append('Read from file: "{}"'.format(audio_filename))
    cmd.append('To Formant (burg): 0, 5, 5500, 0.025, 50')
    cmd.append('Down to Table: "no", "yes", 6, "no", 3, "yes", 3, "yes"')
    cmd.append('Save as tab-separated file: "{}"'.format(formant_filename))
    cmd.append('selectObject: "Sound {}"'.format(name))
    cmd.append('plusObject: "Formant {}"'.format(name))
    cmd.append('plusObject: "Table {}"'.format(name))
    cmd.append('Remove')
    return '\n'.join(cmd)
