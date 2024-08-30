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

def make_stress_dict(items):
    d = {'stress':[],'no_stress':[]}
    for item in items:
        if item.stress == True:d['stress'].append(item)
        elif item.stress == False:d['no_stress'].append(item)
    return d

def select_vowels(language_name, dataset_name = 'COMMON VOICE',
    minimum_n_syllables = 2, number_of_syllables = None, 
    max_n_items_per_speaker = None,
    exclude_diphtong = False, return_stress_dict = False):
    '''
    Collects the stress and no stress vowels for a given language.
    '''
    print('creating query set, for language:',language_name)
    print('dataset:',dataset_name,'minimum_n_syllables:',minimum_n_syllables)
    print('number_of_syllables:',number_of_syllables)
    vowels = select_phonemes(language_name = language_name,
        dataset_name = dataset_name, minimum_n_syllables = minimum_n_syllables,
        number_of_syllables = number_of_syllables, bpc_name = 'vowel')
    if exclude_diphtong:
        print('excluding diphtongs')
        vowels = vowels.exclude(bpcs_str__icontains= 'diphtong')
    if return_stress_dict:
        print('returning stress dict')
        return make_stress_dict(vowels)
    return vowels

def select_phonemes(language_name = None, stress = None, dataset_name = None,
    minimum_n_syllables = None, number_of_syllables = None,
    bpc_name = None, ipa = None,
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
    if number_of_syllables is not None:
        phonemes = phonemes.filter(word__n_syllables = number_of_syllables)
    if max_n_items_per_speaker is not None:
        print('trimming phonemes to maximally',max_n_items_per_speaker,
            'per speaker')
        phonemes = balance_speakers(phonemes, max_n_items_per_speaker)
    return phonemes

def syllables_to_vowels(syllables):
    '''
    Convert a list of syllables to a list of vowels.
    '''
    vowels = []
    for syllable in syllables:
        if len(syllable.vowel) == 0: continue
        vowels.append( syllable.vowel[0] )
    return vowels
    

def select_syllables(language_name = None, dataset_name = 'COMMON VOICE',
    minimum_n_syllables = None, number_of_syllables = None,
    max_n_items_per_speaker = None):
    '''
    Select syllables based on language, dataset and number of syllables.
    '''
    from text.models import Syllable
    syllables = Syllable.objects.all()
    if language_name is not None:
        language = select_language(language_name)
        syllables = syllables.filter(language=language)
    if dataset_name is not None:
        dataset = select_dataset(dataset_name)
        syllables = syllables.filter(dataset=dataset)
    if minimum_n_syllables is not None:
        n = minimum_n_syllables -1
        syllables = syllables.filter(word__n_syllables__gt = n)
    if number_of_syllables is not None:
        syllables = syllables.filter(word__n_syllables = number_of_syllables)
    if max_n_items_per_speaker is not None:
        print('trimming syllables to maximally',max_n_items_per_speaker,
            'per speaker')
        syllables = balance_speakers(syllables, max_n_items_per_speaker)
    return syllables
    
def _filter_words_without_stress_annotation(words):
    output, exclude = [], []
    print('filtering words without stress annotation, returning word list')
    for word in words:
        bad = False
        for syllable in word.syllables:
            if syllable.stress is None: bad = True
        if bad: exclude.append(word)
        else: output.append(word)
    return output, exclude
    
def _remove_words_with_diphtongs(words):
    output, exclude = [], []
    print('removing words with diphtongs, returning word list')
    for word in words:
        bpcs_str = ','.join([x.bpcs_str for x in word.phonemes])
        if 'diphtong' in bpcs_str: exclude.append(word)
        else: output.append(word)
    return output, exclude

def _retain_words_with_one_vowel_per_syllable(words):
    output, exclude = [], []
    print('retaining words with one vowel per syllable, returning word list')
    for word in words:
        syllables = word.syllables
        bad = False
        for syllable in syllables:
            if len(syllable.vowel) != 1: bad = True
        if bad: exclude.append(word) 
        else: output.append(word)
    return output, exclude

def words_to_syllables(words):
    '''
    Convert a list of words to a list of syllables.
    '''
    syllables = []
    for word in words:
        syllables += word.syllables
    return syllables

def select_words(language_name = None, dataset_name = None, 
    minimum_n_syllables = None, number_of_syllables = None, word = None,
    no_diphthongs = False, one_vowel_per_syllable = False, has_stress = False):
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
    if number_of_syllables is not None:
        words = words.filter(n_syllables = number_of_syllables)
    if word is not None:
        words = words.filter(word=word)
    if has_stress:
        words, exclude = _filter_words_without_stress_annotation(words)
        print('excluded words:',len(exclude), 'based on stress annotation')
        print('remaining words:',len(words))
    if no_diphthongs:
        words, exclude = _remove_words_with_diphtongs(words)
        print('excluded words:',len(exclude), 'based on exclusion of diphtongs')
        print('remaining words:',len(words))
    if one_vowel_per_syllable:
        words, exclude = _retain_words_with_one_vowel_per_syllable(words)
        print('excluded words:',len(exclude), 
            'based on words with one vowel per syllable')
        print('remaining words:',len(words))
    return words

def select_language(language_name):
    from text.models import Language
    language = Language.objects.get(language__iexact=language_name)
    return language

def select_bpc(bpc_name):
    from text.models import BPC
    bpc = BPC.objects.get(bpc=bpc_name)
    return bpc

def select_dataset(dataset_name):
    from text.models import Dataset
    dataset = Dataset.objects.get(name__iexact=dataset_name)
    return dataset
