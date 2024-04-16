from utils import load_cgn_textgrids


def make_bpcs():
    '''make a BPCs instance with all broad phonetic classes.'''
    names = 'plosive,nasal,approximant,fricative,voiced,voiceless'
    names += ',high_vowel,mid_vowel,low_vowel,front_vowel,central_vowel'
    names += ',back_vowel,close_vowel,open_vowel'
    names = names.split(',')
    bpcs = 'p t k b d g,n m ŋ ɲ,l r j w ʋ,s ʃ ʒ h f x z v ɣ'
    bpcs += ',b d g m n ŋ ɲ l r j w ʋ ʒ z v'
    bpcs += ',p t k s ʃ h f x ɣ' 
    bpcs += ',i iː ɪ y yː u uː ʉ'
    bpcs += ',ʏ ø øː e eː ɛ ɛː ɛi œy ɑu ɔ o oː ə'
    bpcs += ',a ɑ aː ɒː'
    bpcs += ',i iː ɪ e eː ɛ ɛː ɛi œ œː a'
    bpcs += ',ʉ ɨ ə ɜ ä'
    bpcs += ',u uː ʊ o oː ɔ ɔː ɔi ɑ ɑː ɒ ɒː'
    bpcs = [x.split() for x in bpcs.split(',')]
    return dict(zip(names,bpcs))

def ipa_to_bpc_dict():
    '''return the broad phonetic class of a given IPA symbol.'''
    d = {}
    bpcs = make_bpcs()
    ipas = []
    for bpc in bpcs.values():
        ipas.extend(bpc)
    for ipa in ipas:
        for bpc, phonemes in bpcs.items():
            if not ipa in d.keys(): d[ipa] = []
            if ipa in phonemes and bpc not in d[ipa]: d[ipa].append( bpc ) 
    return d


def make_phoneme_identifier(word, phoneme_index):
    return word.identifier + '_' + str(phoneme_index)

def word_to_phoneme_intervals(speaker,word,textgrid):
    speaker_id = speaker.identifier
    all_phoneme_intervals = textgrid.load()[speaker_id + '_SEG']
    output = []
    for phoneme_interval in all_phoneme_intervals:
        if phoneme_interval.text in ['',' ','sp']: continue
        if '!' in phoneme_interval.text: continue
        start, end = phoneme_interval.xmin, phoneme_interval.xmax
        if start >= word.start_time and end <= word.end_time:
            output.append(phoneme_interval)
    return output

def handle_word(word):
    speaker = word.speaker
    textgrid = audio.textgrid_set.get(phoneme_set_name='cgn')
    phoneme_intervals = word_to_phoneme_intervals(speaker,word,textgrid)
    audio = word.audio
    



def handle_phoneme(phoneme_interval, phoneme_index, word, speaker, audio,
    cgn_to_ipa= None):
    d['identifier'] = make_phoneme_identifier(word, phoneme_index)
    d['phoneme'] = phoneme_interval.text
    d['ipa'] = cgn_to_ipa[phoneme]
    d['word_index'] = phoneme_index
    d['start_time'] = phoneme_interval.xmin
    d['end_time'] = phoneme_interval.xmax
    d['audio'] = audio
    d['bpc'] = ''



'''
    identifier = models.CharField(max_length=100, unique=True, **required)
    word = models.ForeignKey('Word',**dargs)
    index = models.IntegerField(default=None)
    syllable = models.ForeignKey('Syllable',**dargs)
    syllable_index = models.IntegerField(default=None)
    ipa = models.CharField(max_length=10, default='')
    stress = models.BooleanField(default=None, **not_required)
    audio = models.ForeignKey('Audio',**dargs)
    start_time = models.FloatField(default=None, **not_required)
    end_time = models.FloatField(default=None, **not_required)
    bpc = models.CharField(max_length=30, default='')
'''
