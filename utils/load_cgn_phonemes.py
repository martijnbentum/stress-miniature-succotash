from utils import load_cgn_textgrids



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
