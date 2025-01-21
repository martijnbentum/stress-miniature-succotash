from text.models import Dataset, Language

names = 'CGN,COMMON VOICE,COOLEST,MLS,IFADV'
names = names.split(',')

descriptions = []
descriptions.append('Corpus Gesproken Nederlands')
descriptions.append('Mozilla Common Voice dataset')
descriptions.append('Coolest dataset of Dutch lexical stress')
descriptions.append('Multilingual LibriSpeech dataset')
descriptions.append('IFA Dialogue Video corpus')

def get_cv_languages():
    languages = 'Dutch,English,French,German,Italian,Spanish,Polish'
    languages = languages.split(',')
    return Language.objects.filter(language__in=languages)

def get_mls_languages():
    languages = 'Dutch,English,German,Polish'
    languages = languages.split(',')
    return Language.objects.filter(language__in=languages)

language_sets = []
language_sets.append([Language.objects.get(language='Dutch')])
language_sets.append(get_cv_languages())
language_sets.append([Language.objects.get(language='Dutch')])
language_sets.append(get_mls_languages())
language_sets.append([Language.objects.get(language='Dutch')])


def make_datasets():
    for name,description,language_set in zip(names,descriptions, language_sets):
        print(name, description, language_set)
        dataset, created = Dataset.objects.get_or_create(name=name, 
            description=description)
        dataset.languages.add(*language_set)
    return dataset
