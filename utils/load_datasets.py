from text.models import Dataset, Language

names = 'CGN'
names = names.split(',')

descriptions = []
descriptions.append('Corpus Gesproken Nederlands')


language_sets = []
language_sets.append([Language.objects.get(language='Dutch')])

def make_datasets():
    for name,description,language_set in zip(names, descriptions, language_sets):
        dataset, created = Dataset.objects.get_or_create(name=name, 
            description=descriptions)
        if created:
            for language in language_set:
                dataset.languages.add(language)
            dataset.save()
    return dataset
