# experiment to test whether bisyllabic words and combined syllables accross
# word boundaries have distinct representations.

from pathlib import Path
from utils import select

directory = Path('../word_boundary_test')

def load_word_set():
    f = directory / 'bisyllabic_dutch_word_frequency-30-100.txt'
    with f.open('r') as file:
        selected_words = file.read().split('\n')
    from text.models import Word
    words = select.select_words(language_name = 'dutch',  
        number_of_syllables = 2)
    d = {}
    output = []
    for word in words:
        lemma = word.word.lower()
        if lemma not in selected_words: continue
        if lemma in d: d[lemma] += 1
        else: d[lemma] = 1
        if d[lemma] > 30: continue
        output.append(word)
    for k,v in d.items():
        if v < 30: print(k,v,'less than 30')
    return output

def word_set_to_audio_set(words = None):
    if words is None: words = load_word_set()
    audios = []
    for word in words:
        audio = word.audio
        if audio not in audios: audios.append(audio)
    return audios
       
def audios_to_phrase_set(audios = None):
    if audios is None: audios = word_set_to_audio_set()
    phrases = []
    for audio in audios:
        phrase = audio.phrase_set.all()
        if phrase.count() != 1: print('audio has more than one phrase',phrase)
        phrases.append(phrase[0])
    return phrases
    
