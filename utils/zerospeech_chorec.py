from collections import Counter
import json
from progressbar import progressbar
import re
from text.models import Textgrid, Language, Dataset, Speaker
from utils import locations
from utils import needleman_wunch as nw

def handle_chorec(age_range = (6, 11)) :
    print('making sentences')
    sentences = make_sentences(age_range = age_range)
    save_sentences(sentences)
    print('making words')
    words = make_words(sentences)
    save_words(words)
    print('making phonemes')
    phonemes = make_phonemes(sentences)
    save_phonemes(phonemes)

def _make_index_to_word_dict(spoken_words,aligned_spoken_words):
    word_lengths = [len(x.word) +1 for x in spoken_words]
    index = 0
    current_length = word_lengths[index]
    word = spoken_words[index]
    d = {}
    for i, char in enumerate(aligned_spoken_words):
        print(f'{i} word: {char} spoken_word: {word.word} <--- test {index}',
            current_length)
        if char == '-':
            d[i] = word
            continue
        if i >= current_length:
            index += 1
            if index >= len(spoken_words):
                print('index out of range')
            else:
                current_length += word_lengths[index]
                word = spoken_words[index]
        d[i] = word
    print(word_lengths, [x.word for x in spoken_words])
    return d
        
def _align_text_to_spoken(text, spoken_text):
    text = text.replace('<br>', '')
    text= re.sub(r'\s+', ' ', text)
    text, spoken_text  = nw.nw(text, spoken_text).split('\n')
    return text, spoken_text
        

def _find_eos_indices(text, spoken_text):
    index = 0
    indices = []
    text, spoken_text = _align_text_to_spoken(text, spoken_text)
    for char, spoken_char in zip(text, spoken_text):
        # print(f'word: {char} spoken_word: {spoken_char} <--- test')
        if '.' == char or '?' == char or '!' == char:
            indices.append(index) 
            print(f'word: {char} spoken_word: {spoken_char}')
        index += 1
    return indices


def _handle_section(section, speaker):
    st, et = section.xmin, section.xmax
    text = section.text
    words = speaker.word_set.filter(start_time__gte=st, end_time__lte=et)
    spoken_text = ' '.join([w.word for w in words])
    print('\ntext:', text, ' spoken_text:', spoken_text)
    indices = _find_eos_indices(text, spoken_text)
    o = []
    for i in indices:
        # o.append(words[i])
        pass
    print('-')
    return o


def find_eos_words(speaker):
    tg = speaker.textgrid_set.all()[0]
    original_task = tg.load()['original task']
    words = []
    for section in original_task:
        w = _handle_section(section, speaker)
        if w: words.extend(w)
    return words
        
    




def get_speakers(age_range = None, simple_group = None):
    dataset = Dataset.objects.get(name='JASMIN')
    s = Speaker.objects.filter(dataset=dataset)
    if age_range is None and simple_group is None:
        return list(s)
    if age_range:
        s = Speaker.objects.filter(dataset=dataset, age__lte= age_range[1])
        s = s.filter(age__gte=age_range[0])
    if simple_group:
        output = []
        for x in s:
            if x.info_dict['simple_group'] == simple_group:
                output.append(x)
    else: output = list(s)
    return output

def make_sentences(age_range = None, simple_group = None): 
    speakers= get_speakers(age_range = age_range, simple_group = simple_group)
    sentences = []
    error = []
    for speaker in progressbar(speakers):
        try: temp = speaker_to_sentences(speaker)
        except ValueError: error.append(speaker)
        else:sentences.extend(temp)
    if error:
        for s in error:
            print(f'Error with {s.identifier}')
        print('Errors:',len(error))
    return sentences

def make_words(sentences = None):
    words = []
    if not sentences: sentences, error = make_sentences()
    for sentence in progressbar(sentences):
        for i, word in enumerate(sentence.words):
            words.append(Word(word, sentence, i))
    return words

def make_phonemes(sentences = None):
    phonemes = []
    if not sentences: sentences = make_sentences()
    for sentence in progressbar(sentences):
        for i, phoneme in enumerate(sentence.phonemes):
            phonemes.append(Phoneme(phoneme, sentence, i))
    return phonemes 

def save_phonemes(phonemes = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\tphoneme'
    header += '\tprevious_phoneme\tnext_phoneme\tspeaker_id\toverlap'
    header += '\tin_pretraining'
    o = [header]
    if not phonemes: phonemes = make_phonemes(language_name = language_name)
    for phoneme in phonemes:
        o.append(phoneme.line)
    with open(f'../dutch_jasmin_phonemes_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_words(words = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tspeaker_id'
    header += '\toverlap\tin_pretraining'
    o = [header]
    if not words: words = make_words(language_name = language_name)
    for word in words:
        o.append(word.line)
    with open(f'../dutch_jasmin_words_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_sentences(sentences = None, filename = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tidentifier'
    header += '\tspeaker_id\tage\tsimple_group\tgender'
    o = [header]
    if not sentences: sentences = make_sentences(language_name = language_name)
    for sentence in sentences:
        o.append(sentence.line)
    if filename is None:
        filename = f'../dutch_jasmin_sentences_zs.tsv'
    with open(filename,'w') as f:
        f.write('\n'.join(o))
    
def speaker_to_sentences(speaker):
    index = 0
    sentences, temp = [], []
    word_list= list(speaker.word_set.all())
    for word in word_list:
        info = word.info_dict
        temp.append(word)
        if info['eos']:
            sentence = Sentence(temp, speaker, index)
            sentences.append(sentence)
            temp = []
            index += 1
    if temp:
        sentence = Sentence(temp, speaker, index)
        sentences.append(sentence)
    return sentences


class Sentence:
    def __init__(self, words, speaker, index):
        self.words = words
        self.index = index
        self.audio = self.words[0].audio
        self.textgrid = self.audio.textgrid_set.all()[0]
        self.audio_info = json.loads(self.audio.info)
        self.start_time = self.words[0].start_time
        self.end_time = self.words[-1].end_time
        self.audio_filename = self.audio.filename 
        self.identifier = self.audio.filename.split('/')[-1].split('.')[0]
        self.duration = self.end_time - self.start_time
        self.speaker = speaker
        self.speaker_id = self.speaker.identifier
        self.sentence = ' '.join([w.word for w in words])
        self.in_pretraining = False
        self.simple_group = self.speaker.info_dict['simple_group']
        self.gender = self.speaker.gender
        self.age = self.speaker.age

    @property
    def phonemes(self):
        if hasattr(self, '_phonemes'): return self._phonemes
        output = []
        for word in self.words:
            for phoneme in word.phonemes: 
                output.append(IPA(phoneme, word))
        self._phonemes = output
        return self._phonemes
            

    def __repr__(self):
        m = f'{self.identifier} {self.speaker_id} {self.duration:.3f}'
        m += f' {self.sentence}'
        return m

    @property
    def line(self):
        m = f'JASMIN/{self.audio_filename.split("JASMIN/")[-1]}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t"{self.sentence}"' 
        m += f'\t{self.identifier}\t{self.speaker_id}\t{self.age}' 
        m += f'\t{self.simple_group}\t{self.gender}'
        return m

class Word:
    def __init__(self, word, sentence, index):
        self.word = word
        self.sentence = sentence
        self.index = index
        self.filename = sentence.identifier
        self.start_time = word.start_time 
        self.end_time = word.end_time 
        self.duration = self.end_time - self.start_time
        self.speaker_id = sentence.speaker_id

    def __repr__(self):
        m = f'{self.filename} {self.speaker_id} {self.duration:.3f}' 
        m += f' {self.word.word}'
        return m

    @property
    def line(self):
        m = f'{self.filename}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t{self.word.word}'
        m += f'\t{self.speaker_id}\t{self.word.overlap}'
        m += f'\t{self.sentence.in_pretraining}'
        return m

class Phoneme:
    def __init__(self, phoneme, sentence, index):
        self.IPA = phoneme
        self.phoneme_char = phoneme.ipa
        self.start_time = phoneme.start_time - sentence.start_time
        self.end_time = phoneme.end_time - sentence.start_time
        self.duration = self.end_time - self.start_time
        self.sentence = sentence
        self.index = index
        self.filename = sentence.identifier
        self.start_time = phoneme.start_time 
        self.end_time = phoneme.end_time 
        self.duration = self.end_time - self.start_time
        self.speaker_id = sentence.speaker_id
        self.overlap = phoneme.word.overlap

    @property
    def previous_phoneme(self):
        if self.index == 0: return 'SOS'
        return self.sentence.phonemes[self.index - 1].phoneme.ipa

    @property
    def next_phoneme(self):
        if self.index == len(self.sentence.phonemes) - 1: return 'EOS'
        return self.sentence.phonemes[self.index + 1].phoneme.ipa

    @property
    def line(self):
        m = f'{self.filename}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t{self.phoneme_char}'
        m += f'\t{self.previous_phoneme}\t{self.next_phoneme}'
        m += f'\t{self.speaker_id}\t{self.overlap}'
        m += f'\t{self.sentence.in_pretraining}'
        return m


class IPA:
    def __init__(self, phoneme, word):
        self.phoneme= phoneme
        self.ipa = phoneme.ipa
        self.start_time = phoneme.start_time
        self.end_time = phoneme.end_time
        self.duration = phoneme.duration
        self.word = word
        
    def __repr__(self):
        m = f'{self.phoneme} {self.duration:.3f}'
        return m


        
