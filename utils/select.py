import random

def balance_speakers(items, max_n_items_per_speaker = 100):
    '''
    Balance the number of items per speaker.
    '''
    print('shuffling items, will return a list not a queryset')
    random.shuffle(list(items))
    speakers = {}
    output = []
    print('trimming items')
    for item in items:
        speaker_id = item.speaker_id
        if speaker_id not in speakers:
            speakers[speaker_id] = 0
        speakers[speaker_id] += 1
        if speakers[speaker_id] > max_n_items_per_speaker: continue
        output.append(item)
    return output

def select_phonemes(language_name = None, stress = None, dataset_name = None,
    minimum_n_syllables = None, bpc_name = None, ipa = None,
    max_n_items_per_speaker = None):
    '''
    Select phonemes based on language, stress, dataset and number of syllables.
    '''
    from text.models import Phoneme 
    phonemes = Phoneme.objects.all()
    if bpc_name is not None:
        bpc = select_bpc(bpc_name)
        if bpc:
            phonemes = bpc.phoneme_set.all()
        else: print('No bpc found for',bpc_name)
    if language_name is not None:
        language = select_language(language_name)
        phonemes = phonemes.filter(language=language)
    if dataset_name is not None:
        dataset = select_dataset(dataset_name)
        phonemes = phonemes.filter(dataset=dataset)
    if ipa is not None:
        phonemes = phonemes.filter(ipa=ipa)
    if stress is not None:
        phonemes = phonemes.filter(stress=stress)
    if minimum_n_syllables is not None:
        n = minimum_n_syllables -1 
        phonemes = phonemes.filter(word__n_syllables__gt = n)
    if max_n_items_per_speaker is not None:
        print('trimming phonemes to maximally',max_n_items_per_speaker,
            'per speaker')
        phonemes = balance_speakers(phonemes, max_n_items_per_speaker)
    return phonemes


def select_words(language_name = None, dataset_name = None, 
    minimum_n_syllables = None, word = None):
    '''
    Select words based on language, dataset and number of syllables.
    '''
    from text.models import Word
    language = select_language(language_name)
    words = Word.objects.all()
    if language_name is not None:
        language = select_language(language_name)
        words = words.filter(language=language)
    if dataset_name is not None:
        dataset = select_dataset(dataset_name)
        words = words.filter(dataset=dataset)
    if minimum_n_syllables is not None:
        words = words.filter(n_syllables__gt = minimum_n_syllables - 1)
    if word is not None:
        words = words.filter(word=word)
    return words

def select_language(language_name):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language

def select_bpc(bpc_name):
    return None
    from text.models import BPC
    bpc = BPC.objects.get(name__iexact=bpc_name)
    return bpc

def select_dataset(dataset_name):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset
