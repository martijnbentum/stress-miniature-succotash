from progressbar import progressbar
from text.models import Textgrid, Language
from utils import locations

def read_manifest(language_name = 'English'):
    directory = locations.get_language_mls_root_folder(language_name)
    with open(directory / 'train.tsv','r') as f:
        t = [x.split('\t')[0].split('/')[-1] for x in f.read().split('\n') if x]
    return t

def read_meta_data(language_name = 'English'):
    directory = locations.get_language_mls_root_folder(language_name)
    with open(directory / 'metainfo.txt','r') as f:
        t = f.read().split('\n')
    output = []
    for line in t:
        if not line: continue
        temp = line.split('|')
        items = [x.strip() for x in temp]
        if items[1] == 'M': items[1] = 'male'
        elif items[1] == 'F': items[1] = 'female'
        elif items[1] == 'GENDER': 
            output.append(items)
            continue
        else: raise ValueError('unknown value', items[1])
        items[0] = int(items[0])
        items[3] = float(items[3])
        items[4] = int(items[4])
        output.append(items)
    header, data = output[0], output[1:]
    return header, data

def gender_dict():
    header, data = read_meta_data()
    d = {}
    for line in data:
        d[line[0]] = line[1]
    return d

    

def get_textgrids(language_name = 'English'):
    language= Language.objects.get(language__iexact=language_name)
    return Textgrid.objects.filter(audio__language=language)

def make_sentences():
    textgrids = get_textgrids()
    sentences = []
    for textgrid in progressbar(textgrids):
        sentences.extend(textgrid_to_sentence(textgrid))
    return sentences

def make_words(sentences = None):
    words = []
    if not sentences: sentences = make_sentences()
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
    if not phonemes: phonemes = make_phonemes()
    for phoneme in phonemes:
        o.append(phoneme.line)
    with open('../news_phonemes_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_words(words = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tspeaker_id'
    header += '\toverlap\tin_pretraining'
    o = [header]
    if not words: words = make_words()
    for word in words:
        o.append(word.line)
    with open('../news_words_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_sentences(sentences = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tidentifier'
    header += '\tspeaker_id\tin_pretraining'
    o = [header]
    if not sentences: sentences = make_sentences()
    for sentence in sentences:
        o.append(sentence.line)
    with open('../news_sentences_zs.tsv','w') as f:
        f.write('\n'.join(o))
    


def textgrid_to_sentence(textgrid):
    index = 0
    temp = list(textgrid.audio.word_set.all())
    sentence = Sentence(temp, textgrid, index)
    sentences = [sentence]
    return sentences


def check_sentence_in_pretraining(sentence):
    filename = sentence.audio_filename.split('/')[-1]
    manifest = read_manifest()
    return filename in manifest

class Sentence:
    def __init__(self, words, textgrid, index):
        self.words = words
        self.start_time = 0 # words[0].start_time
        self.end_time = textgrid.audio.duration # words[-1].end_time
        self.textgrid = textgrid
        self.index = index
        self.audio = textgrid.audio
        self.audio_filename = self.audio.filename.split('CGN2/')[-1]
        self.identifier = self.audio_filename
        self.duration = self.end_time - self.start_time
        speakers = textgrid.speakers.all()
        if len(speakers) > 1: raise ValueError('More than one speaker')
        self.speaker = speakers[0]
        speaker_id = self.speaker.identifier
        d = gender_dict()
        if speaker_id in d: gender = d[speaker_id]
        else: gender = None
        self.speaker_id = f'{speaker_id}_{gender}' 
        self.sentence = ' '.join([w.word for w in words])
        self.in_pretraining = check_sentence_in_pretraining(self)

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
        return m

    @property
    def line(self):
        m = f'{self.audio_filename}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t"{self.sentence}"' 
        m += f'\t{self.identifier}\t{self.speaker_id}\t{self.in_pretraining}' 
        return m

class Word:
    def __init__(self, word, sentence, index):
        self.word = word
        self.sentence = sentence
        self.index = index
        self.filename = sentence.identifier
        self.start_time = word.start_time - sentence.start_time
        self.end_time = word.end_time - sentence.start_time
        self.duration = self.end_time - self.start_time
        self.speaker_id = str(word.speaker).replace(' ','_')

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
        self.start_time = phoneme.start_time - sentence.start_time
        self.end_time = phoneme.end_time - sentence.start_time
        self.duration = self.end_time - self.start_time
        self.speaker_id = str(phoneme.word.speaker).replace(' ','_')
        self.overlap = phoneme.word.overlap

    @property
    def previous_phoneme(self):
        if self.index == 0: return 'SOS'
        return self.sentence.phonemes[self.index - 1].phoneme

    @property
    def next_phoneme(self):
        if self.index == len(self.sentence.phonemes) - 1: return 'EOS'
        return self.sentence.phonemes[self.index + 1].phoneme

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

        
        

def get_k_words():
    textgrids = get_k_textgrids()
    words = []
    for textgrid in textgrids:
        words.extend(textgrid.word_set.all())
    return words
