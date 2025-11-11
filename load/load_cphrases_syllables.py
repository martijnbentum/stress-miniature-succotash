from . import load_cv_syllables as lcs

def make_syllables():
    from text.models import Language, Dataset
    dataset = Dataset.objects.get(name = 'cgn-phrases')
    language = Language.objects.get(language='Dutch')
    lcs.handle_words(language, dataset)
