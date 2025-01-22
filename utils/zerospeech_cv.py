import json
from progressbar import progressbar
from text.models import Textgrid, Language, Dataset, Speaker
from utils import locations

def handle_language(language_name = 'dutch'):
    print('making sentences')
    sentences = make_sentences(language_name)
    save_sentences(language_name, sentences)
    print('making words')
    words = make_words(sentences, language_name)
    save_words(language_name, words)
    print('making phonemes')
    phonemes = make_phonemes(sentences, language_name)
    save_phonemes(language_name, phonemes)

def read_manifest(language_name = 'dutch'):
    directory = locations.get_language_cv_root_folder(language_name)
    with open(directory / 'cv_train_manifest.tsv','r') as f:
        t = [x.split('\t')[0].split('/')[-1] for x in f.read().split('\n') if x]
    return t

def get_textgrids(language_name = 'dutch'):
    language= Language.objects.get(language__iexact=language_name)
    dataset = Dataset.objects.get(name='COMMON VOICE')
    return Textgrid.objects.filter(audio__language=language, 
        audio__dataset=dataset)

def make_sentences(language_name = 'dutch'): 
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
    header = 'audio_filename\tstart_time\tend_time\tduration\tphoneme'
    header += '\tprevious_phoneme\tnext_phoneme\tspeaker_id\toverlap'
    header += '\tin_pretraining'
    o = [header]
    if not phonemes: phonemes = make_phonemes(language_name = language_name)
    for phoneme in phonemes:
        o.append(phoneme.line)
    with open(f'../{language_name}_cv_phonemes_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_words(language_name, words = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tspeaker_id'
    header += '\toverlap\tin_pretraining'
    o = [header]
    if not words: words = make_words(language_name = language_name)
    for word in words:
        o.append(word.line)
    with open(f'../{language_name}_cv_words_zs.tsv','w') as f:
        f.write('\n'.join(o))

def save_sentences(language_name, sentences = None):
    header = 'audio_filename\tstart_time\tend_time\tduration\ttext\tidentifier'
    header += '\tspeaker_id\tin_pretraining'
    o = [header]
    if not sentences: sentences = make_sentences(language_name = language_name)
    for sentence in sentences:
        o.append(sentence.line)
    with open(f'../{language_name}_cv_sentences_zs.tsv','w') as f:
        f.write('\n'.join(o))
    


def textgrid_to_sentence(textgrid, manifest):
    index = 0
    word_list= list(textgrid.audio.word_set.all())
    sentence = Sentence(word_list, textgrid, index, manifest)
    sentences = [sentence]
    return sentences


def check_sentence_in_pretraining(sentence, manifest):
    filename = sentence.audio_filename.split('/')[-1]
    return filename in manifest


class Sentence:
    def __init__(self, words, textgrid, index, manifest):
        self.words = words
        self.start_time = 0 # words[0].start_time
        self.end_time = textgrid.audio.duration # words[-1].end_time
        self.textgrid = textgrid
        self.index = index
        self.audio = textgrid.audio
        self.audio_filename = self.audio.filename.split('/')[-1]
        self.identifier = self.audio_filename
        self.duration = self.end_time - self.start_time
        speakers = textgrid.speakers.all()
        if len(speakers) > 1: raise ValueError('More than one speaker')
        if len(speakers) == 0: 
            print(f'No speakers for {self.textgrid.identifier}')
            raise ValueError('No speakers')
        self.speaker = speakers[0]
        self.speaker_id = speaker_to_short_id(self.speaker)
        self.sentence = ' '.join([w.word for w in words])
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

def get_speakers(language_name = 'dutch'):
    language = Language.objects.get(language__iexact=language_name)
    dataset = Dataset.objects.get(name='COMMON VOICE')
    temp = Speaker.objects.filter(dataset=dataset)
    speakers = []
    for speaker in temp:
        word = speaker.word_set.first()
        if word.language == language:
            speakers.append(speaker)
    return speakers

def speaker_to_short_id(speaker):
    identifier = speaker.identifier[:9]
    gender = speaker.gender if speaker.gender else ''
    age = speaker.age if speaker.age else ''
    speaker_id = f'{identifier}_{gender}_{age}'
    return speaker_id
        
def load_or_make_common_voice_speaker_dict(language_name = 'dutch'):
    directory = locations.get_language_cv_root_folder(language_name)
    filename = directory / f'zerospeech_{language_name}_speaker_dict.json'
    if filename.exists():
        print('loading speaker dict')
        with open(filename,'r') as f:
            speaker_dict = json.load(f)
        return speaker_dict
    print('making speaker dict')
    speakers = get_speakers(language_name)
    speaker_dict = {}
    for i,speaker in enumerate(speakers):
        speaker_dict[speaker.identifier] = speaker_to_short_id(speaker)
    with open(filename,'w') as f:
        json.dump(speaker_dict,f)
    return speaker_dict
        

