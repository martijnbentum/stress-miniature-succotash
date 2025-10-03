from progressbar import progressbar

def load_all_phrases():
    from text.models import Language, Dataset, Audio
    print('loading language:', language_name)
    language = Language.objects.get(language='Dutch')
    dataset = Dataset.objects.get(name = 'cgn-phrases')
    audios = Audio.objects.filter(language=language, dataset=dataset)
    audios = list(audios)
    n_created = 0
    for audio in progressbar(audios):
        n_created += handle_audio(audio)
    print('loaded audios', audios.count)
    print(f'Created {n_created} phrases in total')

def handle_audio(audio):
    audio_words = get_audio_words(audio)
    phrases = split_audio_words_in_phrases(audio_words)
    n = 0
    for phrase_index, phrase in enumerate(phrases):
        created = handle_phrase(phrase, phrase_index)
        if created: n += 1
    return n

def handle_phrase(phrase_words, phrase_index):
    from text.models import Phrase
    word = phrase_words[0]
    d = {}
    d['identifier'] = make_phrase_identifier(word.audio, phrase_index)
    d['dataset'] = word.dataset
    d['speaker'] = word.speaker
    d['language'] = word.language
    d['index'] = phrase_index
    d['phrase'] = ' '.join([word.word for word in phrase_words])
    d['ipa'] = '|'.join([word.ipa for word in phrase_words])
    d['audio'] = word.audio
    d['start_time'] = phrase_words[0].start_time
    d['end_time'] = phrase_words[-1].end_time
    phrase, created = Phrase.objects.get_or_create(**d)
    for word in phrase_words:
        word.phrase = phrase
        word.save()
    return created

def get_audio_words(audio):
    audio_words = audio.word_set.all()
    audio_words = sorted(audio_words, key=lambda x: x.start_time)
    return audio_words

def split_audio_words_in_phrases(audio_words):
    phrases = []
    phrase = []
    for word in audio_words:
        if word.index == 0:
            if phrase:
                phrases.append(phrase)
                phrase = []
        phrase.append(word)
    if phrase:
        phrases.append(phrase)
    return phrases

def make_phrase_identifier(audio, phrase_index):
    return f'{audio.identifier}_phrase-{phrase_index}'
