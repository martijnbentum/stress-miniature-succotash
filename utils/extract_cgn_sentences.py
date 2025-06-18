import json
import librosa
import os
import pathlib
import random
import subprocess

def load_metadata_file(filename = '../news_books_sentences_zs.tsv'): 
    with open('../news_books_sentences_zs.tsv') as fin:
        t = [x.split('\t') for x in fin.read().split('\n')]
    header = t[0]
    data = t[1:]
    return header, data


def extract_cgn_sentences(metadata_file = '../news_books_sentences_zs.tsv',
    gender = None, comp = None, duration_hours = 10,
    output_dir = '../cgn_sentences/',
    cgn_base_dir = '/vol/bigdata/corpora2/CGN2', overwrite = False):
    random.seed(42)
    comp_name = comp if comp is not None else 'ko'
    gender_name = gender if gender is not None else 'female-male'
    filename = f'../cgn_sentences_{gender_name}_{comp_name}_{duration_hours}.json'
    header, data = load_metadata_file(metadata_file)
    random.shuffle(data)
    if not pathlib.Path(output_dir).exists():
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    sentences = []
    duration = 0
    for line in data:
        if gender is None: pass
        else:
            d = line_to_dict(line)
            if d['gender'] != gender: continue
        if comp is None: pass
        else:
            if line[-1] != comp: continue
        if len(line) < 7: continue  # skip incomplete lines
        d = handle_line(line, output_dir, cgn_base_dir, overwrite=overwrite)
        sentences.append(d)
        duration += d['duration']
        if duration > duration_hours * 3600:
            print(f'stopping after {duration_hours} hours of audio, {duration}')
            break
    write_info(filename, sentences)
    return sentences

def write_info(filename, sentences):
    print(f'writing info to {filename}')
    with open(filename, 'w') as fout:
        json.dump(sentences, fout, indent=4)


def line_to_dict(line, output_dir = '../cgn_sentences/',
    cgn_base_dir = '/vol/bigdata/corpora2/CGN2'):
    d = {}
    d['source_filename'] = f'{cgn_base_dir}/{line[0]}'
    d['source_start'] = float(line[1])
    d['source_end'] = float(line[2])
    d['source_duration'] = float(line[3])
    d['source_transcription'] = line[4]
    d['filename'] = f'{output_dir}{line[5]}'
    try:speaker_id, gender, age = line[6].split('_')
    except ValueError:
        speaker_id, gender, age = None, None, None
    d['speaker_id'] = speaker_id
    d['gender'] = gender
    d['age'] = age
    d['comp'] = line[-1]
    return d

def handle_line(line, output_dir = '../cgn_sentences/', 
    cgn_base_dir = '/vol/bigdata/corpora2/CGN2', overwrite = False):
    d = line_to_dict(line, output_dir, cgn_base_dir)
    extract_audio(d['source_filename'], d['source_start'], d['source_end'], 
        d['filename'], overwrite=overwrite)
    info = audio_file_to_info(d['filename'])
    d['n_channels'] = info['n_channels']
    d['sample_rate'] = info['sample_rate']
    d['samples'] = info['samples']
    d['duration'] = info['duration']
    return d

def extract_audio(input_filename, start, end, output_filename, overwrite=False):
    p = pathlib.Path(output_filename)
    if p.exists() and not overwrite:
        print(f'file {output_filename} already exists, skipping extraction')
        return
    duration = round(end - start, 3)
    command = f'sox {input_filename} {output_filename} trim {start} {duration}'
    os.system(command)
    print(f'extracting audio: {command}')
    

def time_to_samples(time, sr):
    '''convert time to samples'''
    return int(time * sr)

def audio_file_to_info(filename):
    info = soxi_info(filename)
    return soxinfo_to_dict(info)

def _audio_file_to_info(filename):
    info_dict = audio_file_to_info(filename)
    file_id = filename.stem
    return info_dict, file_id

def soxi_info(filename):
    filename = str(filename)
    o = subprocess.run(['sox','--i',filename],stdout=subprocess.PIPE)
    return o.stdout.decode('utf-8')

def clock_to_duration_in_seconds(t):
    hours, minutes, seconds = t.split(':')
    s = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return s

def soxinfo_to_dict(soxinfo):
    x = soxinfo.split('\n')
    d = {}
    d['filename'] = x[1].split(': ')[-1].strip("'")
    d['n_channels'] = int(x[2].split(': ')[-1])
    d['sample_rate'] = int(x[3].split(': ')[-1])
    d['samples'] = int(x[5].split('= ')[-1].split(' sam')[0])
    t = x[5].split(': ')[-1].split(' =')[0]
    d['duration'] = clock_to_duration_in_seconds(t)
    return d

