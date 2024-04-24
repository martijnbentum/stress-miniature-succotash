from utils import load_bpc
from utils import load_cv_textgrids
from utils import maus_phoneme_mapper
from progressbar import progressbar


ipa_to_bpc = load_bpc.ipa_to_bpc_instances(add_longer=True)

def handle_language(language_name):
    from text.models import Language, Dataset
    language = Language.objects.get(language__iexact=language_name)
    dataset = Dataset.objects.get(name = 'COMMON VOICE')
    maus_to_ipa = maus_phoneme_mapper.Maus(language_name).maus_to_ipa()
    handle_words(language, dataset, maus_to_ipa, skip_if_ipa)

def handle_words(language, dataset, maus_to_ipa):
    from text.models import Word
    words = Word.objects.filter(language=language, dataset=dataset)
    n_created = 0
    for word in progressbar(words):
        n_created += handle_word(word, language, maus_to_ipa)
    print('Created', n_created, 'phonemes for', language.language)

def handle_word(word, language, maus_to_ipa):
    speaker = word.speaker
    audio = word.audio
    textgrid = audio.textgrid_set.get(phoneme_set_name='maus')
    syllable_intervals = word_to_syllable_intervals(word,textgrid)
    n_created = 0
    phonemes = word.phoneme_set.all()
    for syllable_index, syllable_interval in enumerate(syllable_intervals):
        syllable, created = handle_syllable(syllable_interval, syllable_index, 
            word, audio, speaker, language, maus_to_ipa)
        if created: n_created += 1
    return n_created

def handle_syllable(syllable_interval, syllable_index, word, audio, speaker,
    language, maus_to_ipa):
    from text.models import Syllable
    d = {}
    d['identifier'] = make_syllable_identifier(word, syllable_index)
    d['phoneme'] = syllable_interval.text
    d['ipa'] = ' '.join([maus_to_ipa[x] for x in d['phoneme'].split(' ')])
    d['word'] = word
    d['index'] = phoneme_index
    d['start_time'] = phoneme_interval.xmin
    d['end_time'] = phoneme_interval.xmax
    d['audio'] = audio
    d['speaker'] = speaker
    d['language'] = language
    syllable, created = Syllable.objects.get_or_create(**d)
    return syllable, created


def make_syllable_identifier(word, syllable_index):
    return word.identifier + '_' + str(phoneme_index)

def select_syllable_phonemes(syllable_interval, phonemes):
    syllable_phonemes = []
    for phoneme in phonemes:
        if contains(phoneme.start_time, phoneme.end_time, 
            syllable_interval.xmin, syllable_interval.xmax):
            syllable_phonemes.append(phoneme)
    if len(syllable_phonemes) != len(syllable_interval.text.split(' ')):
        raise ValueError('mismatched phonemes for syllable',syllable_phonemes)

def contains(smaller_start, smaller_end, larger_start, larger_end):
    return (smaller_start >= larger_start) and (smaller_end <= larger_end)

def word_to_syllable_intervals(word,textgrid):
    all_syllable_intervals = textgrid.load()['MAS']
    output = []
    exclude = ['',' ','sp','[]'] + maus_phoneme_mapper.maus_exclude_phonemes
    for syllable_interval in all_syllable_intervals:
        if syllable_interval.text in exclude: continue
        if '!' in syllable_interval.text: continue
        start, end = syllable_interval.xmin, syllable_interval.xmax
        if start >= word.start_time and end <= word.end_time:
            output.append(syllable_interval)
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
