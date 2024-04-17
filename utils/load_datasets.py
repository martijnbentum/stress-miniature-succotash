from text.models import Dataset, Language

names = 'CGN,COMMON VOICE'
names = names.split(',')

descriptions = []
descriptions.append('Corpus Gesproken Nederlands')
descriptions.append('Mozilla Common Voice dataset')

def get_cv_languages():
    languages = 'Dutch,English,French,German,Italian,Spanish,Polish'
    languages = languages.split(',')
    return Language.objects.filter(language__in=languages)

language_sets = []
language_sets.append([Language.objects.get(language='Dutch')])
language_sets.append(get_cv_languages())


def make_datasets():
    for name,description,language_set in zip(names, descriptions, language_sets):
        dataset, created = Dataset.objects.get_or_create(name=name, 
            description=descriptions)
        if created:
            dataset.languages.add(*language_set)
        else:
            languages = dataset.languages.all()
            for language in language_set:
                if language not in languages:
                    dataset.languages.add(language)
    return dataset
