from pathlib import Path
import sys

# set root folders for datasets

cgn_root = Path('')
ld_root = Path('')
if sys.platform == 'linux':
    ld_root = Path('/vol/tensusers/mbentum/INDEEP/LD')
    cgn_root = Path('/vol/bigdata/corpora2/CGN2')
    ifadv_root = Path('/vol/tensusers/mbentum/IFADV')
    if not ld_root.exists():
        ld_root = Path('/mnt/storage/LD')
        cgn_root = Path('/mnt/storage/CGN/CGN_2.0.3')
elif sys.platform == 'darwin':
    ld_root = Path('/Users/martijn.bentum/Documents/indeep/LD')
    common_voice_root = ld_root
    ifadv_root = Path('/Users/martijn.bentum/IFADV')

common_voice_root = ld_root
baldey_root = ld_root / 'BALDEY'
mald_root = ld_root / 'MALD'
coolest_root = ld_root / 'MALD'
mls_root = Path('/vol/mlusers/mbentum/mls/')

mls_dutch = mls_root / 'dutch'
mls_polish = mls_root / 'polish'
mls_german = mls_root / 'german'
mls_english = mls_root / 'english'
mls_hungarian = mls_root / 'hungarian'

mls_root_folders = [mls_dutch, mls_polish, mls_german, mls_english, mls_hungarian]

def get_language_mls_root_folder(language):
    if language.lower() == 'dutch':
        return mls_dutch
    if language.lower() == 'polish':
        return mls_polish
    if language.lower() == 'german':
        return mls_german
    if language.lower() == 'english':
        return mls_english
    if language.lower() == 'hungarian':
        return mls_hungarian

def get_mls_path(mls_root_folder, folder_name):
    if mls_root_folder not in mls_root_folders: return None
    if folder_name not in ['audio','textgrid','txt']:
        return None
    return mls_root_folder / folder_name

cv_dutch = common_voice_root / 'COMMON_VOICE_DUTCH'
cv_german = common_voice_root / 'COMMON_VOICE_GERMAN'
cv_french = common_voice_root / 'COMMON_VOICE_FRENCH'
cv_hungarian = common_voice_root / 'COMMON_VOICE_HUNGARIAN'
cv_italian = common_voice_root / 'COMMON_VOICE_ITALIAN'
cv_polish = common_voice_root / 'COMMON_VOICE_POLISH'
cv_spanish = common_voice_root / 'COMMON_VOICE_SPANISH'
cv_turkish = common_voice_root / 'COMMON_VOICE_TURKISH'
cv_english = common_voice_root / 'COMMON_VOICE_ENGLISH'

cv_root_folders = [cv_dutch, cv_hungarian, cv_italian, cv_polish, cv_spanish,
    cv_german, cv_french, cv_english] 

def get_language_cv_root_folder(language):
    for cv_root_folder in cv_root_folders:
        l = cv_root_folder.stem.split('_')[-1].lower()
        if l == language: return cv_root_folder
    
def get_cv_path(cv_root_folder, folder_name):
    if cv_root_folder not in cv_root_folders: return None
    if folder_name not in 'textgrids,clips,transcriptions'.split(','):
        return None
    return cv_root_folder / folder_name

#CGN 
cgn_data = cgn_root / 'data'
cgn_audio = cgn_data / 'audio/wav'
cgn_speaker_file = cgn_data / 'meta/text/speakers.txt'
# cgn transcription root
cgn_transcription = Path('/vol/tensusers/mbentum/CGN_AUDIO_EXTRACT')
cgn_awd = cgn_transcription / 'awd'
cgn_ort = cgn_transcription / 'ort'
cgn_fon = cgn_transcription / 'fon'

def cgn_audio_files(comps = 'abefghijklno',languages = ['nl','fl']):
    '''loads audio files from CGN corpus.
    components represent the different parts of the corpus.
    languages represent the languages in the corpus. Netherlandic and Flemish
    Dutch.
    '''
    audio_filenames = []
    for comp in comps:
        for language in languages:
            pa = 'comp-' + comp + '/' + language
            p = cgn_audio / pa
            af = p.glob('*.wav')
            af = [{'filename':f,'identifier':f.stem,
                'component':comp,'language':language} for f in af]
            audio_filenames.extend(af)
    return audio_filenames


coolest_root = ld_root / 'COOLEST'
coolest_audio = coolest_root / 'Recordings'
#coolest_textgrids = coolest_root / 'TextGrids corrected'
coolest_textgrids = coolest_root / 'mauser_textgrids'

ifadv_audio = ifadv_root / 'TURNS'
ifadv_textgrids = ifadv_root / 'MAUSER_TURNS_TEXTGRIDS'
ifadv_speaker_info = ifadv_root / 'speaker_id_to_speaker_info_dict.json'
filename =  ifadv_root / 'turn_wav_filename_to_speaker_id.json'
ifadv_audio_file_to_speaker_id = filename
filename = ifadv_root / 'turn_wav_filename_to_start_time_dict.json'
ifadv_audio_file_to_start_time = filename
filename = ifadv_root / 'turn_wav_filename_to_overlap_dict.json'
ifadv_audio_file_to_overlap = filename
    
    
    
    

celex_directory = '../CELEX/'
celex_english_phonology_file = celex_directory+ 'EPW.CD'
celex_dutch_phonology_file = celex_directory + 'DPW.CD'
celex_german_phonology_file = celex_directory + 'GPW.CD'

formants_dir = Path('../formants/')

hidden_states_dir = Path('../hidden_states/')
if sys.platform == 'linux':
    hidden_states_dir = Path('/vol/mlusers/mbentum/indeep/hidden_states/')

language_naudios_dict = Path('../language_naudios_dict.json')

classifier_dir = Path('../classifiers/')
dataset_dir = Path('../dataset/')
if sys.platform == 'linux':
    classifier_dir = Path('/vol/mlusers/mbentum/indeep/classifiers/')
    dataset_dir = Path('/vol/mlusers/mbentum/indeep/dataset/')
        

finetuned_dir = Path('/vol/tensusers3/mbentum/finetune/')
dutch_sampa_xlsr_dir = finetuned_dir / 'sampa_xlsr_300m/checkpoint-15300/'
fd = finetuned_dir
dutch_orthographic_xlsr_dir = fd / 'orthographic_xlsr_300m/checkpoint-13671/'

st_phonetics_base = Path('/vol/mlusers/mbentum/st_phonetics/')
st_phonetics_codebooks = st_phonetics_base / 'codebooks'
name = 'audio_to_hidden_state_number_dict.json'
st_phonetics_audio_to_hidden_state_number_dict = st_phonetics_base / name


# Jasmin
jasmin_root = Path('/vol/bigdata/corpora/JASMIN')
jasmin_audio_dirs = []    
jasmin_awd_dirs = []
for i in range(1,7):
    jasmin_audio_dirs.append( jasmin_root / f'DVD0{i}/data/audio/wav')
    jasmin_awd_dirs.append( jasmin_root / f'DVD0{i}/data/annot/text/awd')
jasmin_comp_p_audio_files = []
jasmin_comp_q_audio_files = []
for d in jasmin_audio_dirs:
    p = d / 'comp-p'
    q = d / 'comp-q'
    jasmin_comp_p_audio_files.extend(list(p.glob('*/*.wav')))
    jasmin_comp_q_audio_files.extend(list(q.glob('*/*.wav')))
jasmin_comp_p_awd_files = []
jasmin_comp_q_awd_files = []
for d in jasmin_awd_dirs:
    p = d / 'comp-p'
    q = d / 'comp-q'
    jasmin_comp_p_awd_files.extend(list(p.glob('*/*.awd')))
    jasmin_comp_q_awd_files.extend(list(q.glob('*/*.awd')))

jasmin_dutch_speaker_file = jasmin_root / 'CDdoc/data/meta/text/nl/speakers.txt'
jasmin_flemish_speaker_file = jasmin_root / 'CDdoc/data/meta/text/vl/speakers.txt'
jasmin_countries_file = jasmin_root / 'CDdoc/doc/countries.txt'
jasmin_languages_file = jasmin_root / 'CDdoc/doc/languages.txt'

#chorec
chorec_root = Path('/vol/bigdata/corpora/CHOREC-1.0')
chorec_data = chorec_root / 'data'
chorec_doc = chorec_root / 'doc'
chorec_meta = chorec_doc / 'Metadata'
chorec_audio_files = chorec_data.glob('*/*/*AVI*.wav')  
chorec_textgrid_files = chorec_data.glob('*/*/*AVI*a*.TextGrid')
chorec_speaker_info_files = chorec_meta.glob('SpeakerInfo*.xls')

    
