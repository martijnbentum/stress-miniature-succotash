from progressbar import progressbar
from text.models import Textgrid, Language
from utils import locations

def handle_language(language_name):
    print('making sentences')
    sentences = make_sentences(language_name)
    print('making words')
    words = make_words(sentences, language_name)
    save_words(language_name, words)
    print('making phonemes')
    phonemes = make_phonemes(sentences, language_name)
    save_phonemes(language_name, phonemes)

def read_manifest(language_name):
    directory = locations.get_language_mls_root_folder(language_name)
    with open(directory / 'train.tsv','r') as f:
        t = [x.split('\t')[0].split('/')[-1] for x in f.read().split('\n') if x]
    output = []
    for line in t:
        if 'fn' in line:continue
        if 'fv' in line:continue
        if 'common voice' in line:continue
        output.append(line)
    return output

def read_meta_data(language_name):
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

def gender_dict(language_name):
    header, data = read_meta_data(language_name)
    d = {}
    for line in data:
        d[line[0]] = line[1]
    return d

def audiofilename_to_split(audio_filename):
    if 'train' in audio_filename: return 'train'
    if 'dev' in audio_filename: return 'dev'
    if 'test' in audio_filename: return 'test'
    raise ValueError('unknown split', audio_filename)


def get_textgrids(language_name):
    language= Language.objects.get(language__iexact=language_name)
    return Textgrid.objects.filter(audio__language=language)

def make_sentences(language_name): 
    manifest = read_manifest(language_name)
    textgrids = get_textgrids(language_name)
    sentences = []
    error = []
    for textgrid in progressbar(textgrids):
        try: temp = textgrid_to_sentence(textgrid, manifest)
        except ValueError: error.append(textgrid)
        else:sentences.extend(temp)
    if error:
        for tg in error:
            print(f'Error with {tg.identifier}')
        print('Errors:',len(error))
    return sentences

def make_words(sentences = None,language_name = ''):
    words = []
    if not sentences: sentences, error = make_sentences(language_name)
    for sentence in progressbar(sentences):
        for i, word in enumerate(sentence.words):
            words.append(Word(word, sentence, i))
    return words

def make_phonemes(sentences = None,language_name = ''):
    phonemes = []
    if not sentences: sentences = make_sentences()
    for sentence in progressbar(sentences):
        for i, phoneme in enumerate(sentence.phonemes):
            phonemes.append(Phoneme(phoneme, sentence, i))
    return phonemes 


def save_phonemes(language_name, phonemes = None):
    if not phonemes: phonemes = make_phonemes(language_name = language_name)
    o = [phonemes[0].header]
    for phoneme in phonemes:
        o.append(phoneme.line)
    with open(f'../{language_name}_mls_phonemes_zs.tsv','w') as f:
        f.write('\n'.join(o))


def save_words(language_name, words = None):
    if not words: words = make_words(language_name = language_name)
    o = [words[0].header]
    for word in words:
        o.append(word.line)
    with open(f'../{language_name}_mls_words_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_sentences(language_name, sentences = None):
    if not sentences: sentences = make_sentences(language_name = language_name)
    o = [sentences[0].header]
    for sentence in sentences:
        o.append(sentence.line)
    with open(f'../{language_name}_mls_sentences_zs.tsv','w') as f:
        f.write('\n'.join(o))
    


def textgrid_to_sentence(textgrid, manifest):
    index = 0
    word_list= list(textgrid.audio.word_set.all())
    sentence = Sentence(word_list, textgrid, index, manifest)
    sentences = [sentence]
    return sentences


def check_sentence_in_pretraining(sentence, manifest):
    filename = sentence.audio_filename
    return filename in manifest

class Sentence:
    def __init__(self, words, textgrid, index, manifest):
        self.words = words
        self.nwords = len(words)
        self.start_time = 0 # words[0].start_time
        self.end_time = textgrid.audio.duration # words[-1].end_time
        self.textgrid = textgrid
        self.index = index
        self.audio = textgrid.audio
        self.split = audiofilename_to_split(self.audio.filename)
        self.audio_filename = self.audio.filename.split('/')[-1]
        self.identifier = textgrid.identifier
        self.duration = self.end_time - self.start_time
        speakers = textgrid.speakers.all()
        if len(speakers) > 1: raise ValueError('More than one speaker')
        if len(speakers) == 0: 
            print(f'No speakers for {self.textgrid.identifier}')
            raise ValueError('No speakers')
        self.speaker = speakers[0]
        self.gender = self.speaker.gender
        speaker_id = self.speaker.identifier
        self.speaker_id = f'{speaker_id}_{self.gender}' 
        self.sentence = ' '.join([w.word for w in words])
        self.phon_sentence = ' '.join([p.ipa for p in self.phonemes])
        self.in_pretraining = check_sentence_in_pretraining(self, manifest)

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
    def header(self):
        h= 'audio_filename\tidentifier\tstart_time\tend_time'
        h+= '\tduration\ttext\tsplit\tn_words\tspeaker_id'
        h+= '\tin_pretraining'
        return h

    @property
    def line(self):
        m = f'{self.audio_filename}\t{self.identifier}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t"{self.sentence}"'
        m += f'\t{self.split}' 
        m += f'\t{self.nwords}\t{self.speaker_id}\t{self.in_pretraining}' 
        return m

    @property
    def show(self):
        show(self.header, self.line)

class Word:
    def __init__(self, word, sentence, index):
        self.word = word
        self.sentence = sentence
        self.index = index
        self.audio_filename = sentence.audio_filename
        self.identifier = word.identifier
        self.start_time = word.start_time - sentence.start_time
        self.end_time = word.end_time - sentence.start_time
        self.duration = self.end_time - self.start_time
        self.speaker_id = sentence.speaker_id
        self.phones = ' '.join([p.ipa for p in word.phonemes])
        self.n_phones = len(word.phonemes)

    def __repr__(self):
        m = f'{self.filename} {self.speaker_id} {self.duration:.3f}' 
        m += f' {self.word.word}'
        return m

    @property
    def header(self):
        h= 'audio_filename\tidentifier\tstart_time\tend_time\tduration'
        h+= '\ttext\tphones\tn_phones\tsplit\tword_index\tsentence_identifier'
        h+= '\tspeaker_id\tin_pretraining'
        return h

    @property
    def line(self):
        m = f'{self.audio_filename}\t{self.identifier}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t{self.word.word}'
        m += f'\t{self.phones}\t{self.n_phones}\t{self.sentence.split}'
        m += f'\t{self.index}\t{self.sentence.identifier}'
        m += f'\t{self.speaker_id}'
        m += f'\t{self.sentence.in_pretraining}'
        return m

    @property
    def show(self):
        show(self.header, self.line)

class Phoneme:
    def __init__(self, phoneme, sentence, index):
        self.IPA = phoneme
        self.word = phoneme.word
        self.phones = ' '.join([p.ipa for p in self.word.phonemes])
        self.phone_index = self.word.phonemes.index(phoneme.phoneme)
        self.phoneme_char = phoneme.ipa
        self.start_time = phoneme.start_time - sentence.start_time
        self.end_time = phoneme.end_time - sentence.start_time
        self.duration = self.end_time - self.start_time
        self.sentence = sentence
        self.index = index
        self.audio_filename = sentence.audio_filename
        self.identifier = phoneme.phoneme.identifier
        self.start_time = phoneme.start_time - sentence.start_time
        self.end_time = phoneme.end_time - sentence.start_time
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
    def header(self):
        h= 'audio_filename\tidentifier\tstart_time\tend_time'
        h+= '\tduration\tphone\tprevious_phone\tnext_phone'
        h+= '\tphone_index\tword_index\tword_identifier\tsentence_identifier'
        h+= '\tspeaker_id\tin_pretraining'
        return h

    @property
    def line(self):
        m = f'{self.audio_filename}\t{self.identifier}'
        m += f'\t{self.start_time:.3f}\t{self.end_time:.3f}'
        m += f'\t{self.duration:.3f}\t{self.phoneme_char}'
        m += f'\t{self.previous_phoneme}\t{self.next_phoneme}'
        m += f'\t{self.phone_index}\t{self.word.index}'
        m += f'\t{self.word.identifier}\t{self.sentence.identifier}'
        m += f'\t{self.speaker_id}'
        m += f'\t{self.sentence.in_pretraining}'
        return m

    @property
    def show(self):
        show(self.header, self.line)


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

def show(header,line):
    for h,l in zip(header.split('\t'),line.split('\t')):
        print(f'{h}: {l}')
    print('header:',len(header.split('\t')), '\nline:',len(line.split('\t')))
        
