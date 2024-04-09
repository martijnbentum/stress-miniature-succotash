from text.models import Language

languages = 'Dutch'
languages = languages.split(',')

isos = 'nl'
isos = isos.split(',')

def make_languages():
    for iso,language in zip(isos, languages):
        Language.objects.get_or_create(language=language, iso=iso)
