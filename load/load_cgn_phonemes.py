from load import load_cgn_textgrids
from load import load_bpc
from utils import phoneme_mapper
from progressbar import progressbar


cgn_to_ipa = phoneme_mapper.Mapper('dutch').cgn_to_ipa
ipa_to_bpc = load_bpc.ipa_to_bpc_instances(add_longer=True)

def make_phoneme_identifier(word, phoneme_index):
    return word.identifier + '_' + str(phoneme_index)

def word_to_phoneme_intervals(speaker,word,textgrid):
    speaker_id = speaker.identifier
    all_phoneme_intervals = textgrid.load()[speaker_id + '_SEG']
    output = []
    for phoneme_interval in all_phoneme_intervals:
        if phoneme_interval.text in ['',' ','sp','[]','#']: continue
        if '!' in phoneme_interval.text: continue
        start, end = phoneme_interval.xmin, phoneme_interval.xmax
        if start >= word.start_time and end <= word.end_time:
            output.append(phoneme_interval)
    return output

def handle_word(word, language):
    speaker = word.speaker
    audio = word.audio
    textgrid = audio.textgrid_set.get(phoneme_set_name='cgn')
    phoneme_intervals = word_to_phoneme_intervals(speaker,word,textgrid)
    n_created = 0
    phonemes = []
    for phoneme_index, phoneme_interval in enumerate(phoneme_intervals):
        phoneme, created = handle_phoneme(phoneme_interval, phoneme_index, 
            word, audio, speaker, language)
        if created: n_created += 1
        phonemes.append(phoneme)
        ipa = [phoneme.ipa for phoneme in phonemes]
        word.ipa = ' '.join(ipa)
        word.save()
    return n_created
        
    
def load_all_phonemes(start_index = 0, skip_if_ipa = True):
    from text.models import Language, Word
    dutch = Language.objects.get(language='Dutch')
    words = Word.objects.filter(dataset__name='CGN', language=dutch)
    n_created = 0
    for word in progressbar(words[start_index:]):
        if skip_if_ipa and word.ipa: continue
        n_created += handle_word(word, dutch)
    print('Created', n_created, 'phonemes.')

def handle_phoneme(phoneme_interval, phoneme_index, word, audio, speaker,
    language, check_bpcs = False):
    from text.models import Phoneme
    d = {}
    d['identifier'] = make_phoneme_identifier(word, phoneme_index)
    d['phoneme'] = phoneme_interval.text
    d['ipa'] = cgn_to_ipa[d['phoneme']]
    d['word'] = word
    d['word_index'] = phoneme_index
    d['start_time'] = phoneme_interval.xmin
    d['end_time'] = phoneme_interval.xmax
    d['audio'] = audio
    d['speaker'] = speaker
    d['language'] = language
    bpcs = ipa_to_bpc[d['ipa']]
    d['bpcs_str'] = ','.join([bpc.bpc for bpc in bpcs])
    phoneme, created = Phoneme.objects.get_or_create(**d)
    phoneme.bpcs.add(*bpcs)
    return phoneme, created



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
