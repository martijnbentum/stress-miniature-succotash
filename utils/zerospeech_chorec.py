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

def get_speakers(age_range = None):
    dataset = Dataset.objects.get(name='CHOREC')
    s = Speaker.objects.filter(dataset=dataset)
    if age_range:
        s = Speaker.objects.filter(dataset=dataset, age__lte= age_range[1])
        s = s.filter(age__gte=age_range[0])
    return list(s)

def make_sentences(age_range = None): 
    speakers= get_speakers(age_range = age_range)
    sentences = []
    error = []
    for speaker in progressbar(speakers):
        try: temp = speaker_to_sentences(speaker)
        except ValueError as e: error.append((speaker,e))
        else:sentences.extend(temp)
    if error:
        for line in error:
            s, e = line
            print(f'Error with {s.identifier}, {e}')
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
    with open(f'../dutch_chorec_phonemes_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_words(words = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tspeaker_id'
    header += '\toverlap\tin_pretraining'
    o = [header]
    if not words: words = make_words(language_name = language_name)
    for word in words:
        o.append(word.line)
    with open(f'../dutch_chorec_words_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_sentences(sentences = None, filename = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tidentifier'
    header += '\tspeaker_id\tage\tgender'
    o = [header]
    if not sentences: sentences = make_sentences(language_name = language_name)
    for sentence in sentences:
        o.append(sentence.line)
    if filename is None:
        filename = f'../dutch_chorec_sentences_zs.tsv'
    with open(filename,'w') as f:
        f.write('\n'.join(o))

def speaker_to_sentences(speaker):
    index = 0
    sentences, temp = [], []
    word_list= list(speaker.word_set.all())
    if word_list == []: 
        m = f'No words for speaker {speaker.identifier}'
        raise ValueError(m)
    last_audio_id = word_list[0].audio.identifier
    last_start_time = word_list[0].start_time
    for word in word_list:
        info = word.info_dict
        if (info['eos'] or word.audio.identifier != last_audio_id) and temp:
            if word.audio.identifier == last_audio_id:
                temp.append(word)
            sentence = Sentence(temp, speaker, index)
            sentences.append(sentence)
            index += 1
            if word.audio.identifier == last_audio_id: temp = []
            else: temp = [word]
        else: temp.append(word)
        last_audio_id = word.audio.identifier

    if temp:
        sentence = Sentence(temp, speaker, index)
        sentences.append(sentence)
    used_words = []
    for sentence in sentences:
        used_words.extend(sentence.words)
    if len(used_words) != len(word_list):
        raise ValueError(f'Not all words used for speaker {speaker}')
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
        m = f'CHOREC-1.0/{self.audio_filename.split("CHOREC-1.0/")[-1]}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t"{self.sentence}"' 
        m += f'\t{self.identifier}\t{self.speaker_id}\t{self.age}' 
        m += f'\t{self.gender}'
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


        

def _handle_section(section, speaker):
    st, et = section.xmin, section.xmax
    text = section.text
    words = list(speaker.word_set.filter(start_time__gte=st, end_time__lte=et))
    final_word = words[-1]
    info = final_word.info_dict
    info['eos'] = True
    final_word.info = json.dumps(info)
    final_word.save()
    return final_word


def set_eos_words(speaker):
    try:
        tg = speaker.textgrid_set.all()[0]
    except IndexError:
        print(f'No textgrid for {speaker.identifier}')
        return
    original_task = tg.load()['original task']
    words = []
    for section in original_task:
        w = _handle_section(section, speaker)
        if w: words.append(w)
    return words

def set_eos_words_for_all_chorec_speakers():
    speakers = get_speakers()
    for speaker in speakers:
        set_eos_words(speaker)
    print('Done setting EOS for all chorec speakers')
