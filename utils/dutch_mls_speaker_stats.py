import json
import matplotlib.pyplot as plt
from text.models import Speaker, Dataset, Language
from pathlib import Path
from progressbar import progressbar

dutch = Language.objects.get(language='Dutch')
mls = Dataset.objects.get(name='MLS')

def get_all_speakers():
    return Speaker.objects.filter(dataset=mls)

def speaker_to_audios(speaker):
    textgrids = speaker.textgrid_set.filter(audio__language = dutch)
    audios = [tg.audio for tg in textgrids]
    return audios

def speaker_to_stats(speaker):
    print('handling speaker:', speaker.identifier)
    audios = speaker_to_audios(speaker)
    durations = [audio.duration for audio in audios if audio is not None]
    total_duration = sum(durations) / 3600
    return total_duration

def make_or_load_speaker_stats():
    p = Path('../dutch_mls_speaker_stats.json')
    if p.exists():
        with p.open() as f:
            return json.load(f)
    speakers = get_all_speakers()
    speaker_stats = {}
    for speaker in progressbar(speakers):
        total_duration = speaker_to_stats(speaker)
        speaker_stats[speaker.identifier] = total_duration
    with p.open('w') as f:
        json.dump(speaker_stats, f, indent=4)
    return speaker_stats

def load_metadata():
    p = Path('../dutch/metadata.txt')
    with p.open() as f:
        t = [x.split('|') for x in f.read().split('\n') if x]
    for line in t:
        if len(line) != 7: continue
        for j,item in enumerate(line):
            line[j] = item.strip()
    header = t[0]
    data = t[1:]
    for line in data:
        for j,item in enumerate(line):
            column_name = header[j]
            if column_name == 'MINUTES':
                line[j] = round(float(item) * 60,3)
    header[header.index('MINUTES')] = 'SECONDS'
    return header, data

def make_or_load_book_stats(overwrite=False):
    p = Path('../dutch_mls_stats.json')
    if p.exists() and not overwrite:
        print('Loading existing book stats from:', p)
        with p.open() as f:
            return json.load(f)
    header, data = load_metadata()
    speaker_index = header.index('SPEAKER')
    book_index = header.index('BOOK ID')
    duration_index = header.index('SECONDS')
    gender_index = header.index('GENDER')
    d = {}
    for line in data:
        speaker_id = line[speaker_index]
        book_id = line[book_index]
        if speaker_id not in d:
            d[speaker_id] = {'duration':0, 'gender': line[gender_index]} 
        if book_id not in d[speaker_id]:
            d[speaker_id][book_id] = line[duration_index]
        else:
            d[speaker_id][book_id] += line[duration_index]
        d[speaker_id]['duration'] += line[duration_index]
    with p.open('w') as f:
        json.dump(d, f, indent=4)
    return d

def plot_speaker_book_materials(speaker_id):
    d = make_or_load_book_stats()
    speaker_id = str(speaker_id)
    d = d[speaker_id]
    plt.clf()
    plt.hist([v/3600 for k,v in d.items() if k not in ['duration','gender']], 
        bins=20)
    plt.xlabel('hours per book')
    plt.ylabel('n books')
    plt.grid(alpha = .5) 
    title = f'Speaker {speaker_id} book durations (gender: {d["gender"]})'
    title += f'\nTotal duration: {d["duration"]/3600:.2f} hours'
    plt.title(title)
    plt.show()
    
    




    
