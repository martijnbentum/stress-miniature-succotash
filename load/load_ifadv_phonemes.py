from load import load_bpc
from utils import maus_phoneme_mapper
from progressbar import progressbar
 
ipa_to_bpc = load_bpc.ipa_to_bpc_instances(add_longer=True)

def make_all_phonemes(skip_if_ipa = True):
    from text.models import Language, Dataset
    language = Language.objects.get(language__iexact='dutch')
    dataset = Dataset.objects.get(name = 'IFADV')
    maus_to_ipa = maus_phoneme_mapper.Maus('dutch').maus_to_ipa()
    handle_words(language, dataset, maus_to_ipa, skip_if_ipa)

def handle_words(language, dataset, maus_to_ipa, skip_if_ipa = True):
    from text.models import Word
    words = Word.objects.filter(language=language, dataset=dataset)
    n_created = 0
    for word in progressbar(words):
        if skip_if_ipa and word.ipa: continue
        n_created += handle_word(word, language, maus_to_ipa, dataset)
    print('Created', n_created, 'phonemes for', language.language)

def handle_word(word, language, maus_to_ipa, dataset):
    speaker = word.speaker
    audio = word.audio
    textgrid = audio.textgrid_set.get(phoneme_set_name='maus')
    phoneme_intervals = word_to_phoneme_intervals(speaker,word,textgrid)
    n_created = 0
    phonemes = []
    for phoneme_index, phoneme_interval in enumerate(phoneme_intervals):
        phoneme, created = handle_phoneme(phoneme_interval, phoneme_index, 
            word, audio, speaker, language, maus_to_ipa, dataset)
        if created: n_created += 1
        phonemes.append(phoneme)
        ipa = [phoneme.ipa for phoneme in phonemes]
        word.ipa = ' '.join(ipa)
        word.save()
    return n_created

def handle_phoneme(phoneme_interval, phoneme_index, word, audio, speaker,
    language, maus_to_ipa, dataset):
    from text.models import Phoneme
    d = {}
    d['identifier'] = make_phoneme_identifier(word, phoneme_index)
    d['phoneme'] = phoneme_interval.text
    d['ipa'] = maus_to_ipa[d['phoneme']]
    d['word'] = word
    d['word_index'] = phoneme_index
    d['start_time'] = phoneme_interval.xmin
    d['end_time'] = phoneme_interval.xmax
    d['audio'] = audio
    d['speaker'] = speaker
    d['language'] = language
    d['dataset'] = dataset
    bpcs = ipa_to_bpc[d['ipa']]
    d['bpcs_str'] = ','.join([bpc.bpc for bpc in bpcs])
    phoneme, created = Phoneme.objects.get_or_create(**d)
    phoneme.bpcs.add(*bpcs)
    return phoneme, created


def make_phoneme_identifier(word, phoneme_index):
    return word.identifier + '_' + str(phoneme_index)

def word_to_phoneme_intervals(speaker,word,textgrid):
    speaker_id = speaker.identifier
    all_phoneme_intervals = textgrid.load()['MAU']
    output = []
    exclude = ['',' ','sp','[]'] + maus_phoneme_mapper.maus_exclude_phonemes
    for phoneme_interval in all_phoneme_intervals:
        if phoneme_interval.text in exclude: continue
        if '!' in phoneme_interval.text: continue
        start, end = phoneme_interval.xmin, phoneme_interval.xmax
        if start >= word.start_time and end <= word.end_time:
            output.append(phoneme_interval)
    return output


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
