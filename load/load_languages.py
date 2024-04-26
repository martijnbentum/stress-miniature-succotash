from text.models import Language

languages = 'Dutch,English,French,German,Italian,Spanish,Polish,Hungarian'
languages = languages.split(',')

isos = 'nl,en,fr,de,it,es,pl,hu'
isos = isos.split(',')

def make_languages():
    for iso,language in zip(isos, languages):
        Language.objects.get_or_create(language=language, iso=iso)
