from pathlib import Path
import sys

# set root folders for datasets

cgn_root = Path('')
ld_root = Path('')
if sys.platform == 'linux':
    ld_root = Path('/vol/tensusers/mbentum/INDEEP/LD')
    cgn_root = Path('/vol/bigdata/corpora2/CGN2')
    if not ld_root.exists():
        ld_root = Path('/mnt/storage/LD')
        cgn_root = Path('/mnt/storage/CGN/CGN_2.0.3')
elif sys.platform == 'darwin':
    ld_root = Path('/Users/martijn.bentum/Documents/indeep/LD')
    common_voice_root = ld_root

common_voice_root = ld_root
baldey_root = ld_root / 'BALDEY'
mald_root = ld_root / 'MALD'
coolest_root = ld_root / 'MALD'

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
    cv_german, cv_french] 

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

celex_directory = '../CELEX/'
celex_english_phonology_file = celex_directory+ 'EPW.CD'
celex_dutch_phonology_file = celex_directory + 'DPW.CD'
celex_german_phonology_file = celex_directory + 'GPW.CD'
