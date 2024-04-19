from utils import locations, maus_phoneme_mapper, load_bpc
import textgrids

def textgrid_filenames(language_name):
    root_folder = locations.get_language_cv_root_folder(language_name)
    textgrid_folder = locations.get_cv_path(root_folder, 'textgrids')
    return list(textgrid_folder.glob('*.TextGrid'))

def collect_phonemes(language_name):
    phonemes = {}
    m = maus_phoneme_mapper.Maus(language_name)
    maus_to_ipa = m.maus_to_ipa()
    phonemes = {ipa:0 for ipa in maus_to_ipa.values()}
    for filename in textgrid_filenames(language_name):
        tg = textgrids.TextGrid(filename)
        for interval in tg['MAU']:
            if interval.text in maus_phoneme_mapper.maus_exclude_phonemes:
                continue
            phoneme = maus_to_ipa[interval.text]
            phonemes[phoneme] += 1
    return phonemes

def check_bpcs(language_name, phonemes = None):
    if not phonemes: phonemes = collect_phonemes(language_name)
    m = maus_phoneme_mapper.Maus(language_name)
    d = load_bpc.ipa_to_bpc_dict()
    for ipa, count in phonemes.items():
        if count == 0: continue
        if ipa not in d.keys():
            print(ipa, count, language_name)
            print(m.ipa_to_lines()[ipa])
            print('-')

def check_bpcs_all_languages():
    for cv_root_folder in locations.cv_root_folders:
        language = cv_root_folder.stem.split('_')[-1].lower()
        print('handling', language)
        check_bpcs(language)

