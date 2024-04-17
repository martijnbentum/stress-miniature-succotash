from pathlib import Path
import sys

# set root folders for datasets

cgn_root = Path('')
ld_root = Path('')
if sys.platform == 'linux':
    ld_root = Path('/vol/tensusers/mbentum/INDEEP/LD')
    cgn_root = Path('/vol/bigdata/corpora2/CGN2')
elif sys.platform == 'darwin':
    ld_root = Path('/Users/martijn.bentum/Documents/indeep/LD')
    common_voice_root = ld_root

common_voice_root = ld_root
baldey_root = ld_root / 'BALDEY'
mald_root = ld_root / 'MALD'
coolest_root = ld_root / 'MALD'

cv_dutch = common_voice_root / 'COMMON_VOICE_DUTCH'
cv_hungarian = common_voice_root / 'COMMON_VOICE_HUNGARIAN'
cv_italian = common_voice_root / 'COMMON_VOICE_ITALIAN'
cv_polish = common_voice_root / 'COMMON_VOICE_POLISH'
cv_spanish = common_voice_root / 'COMMON_VOICE_SPANISH'
cv_turkish = common_voice_root / 'COMMON_VOICE_TURKISH'

cv_root_folders = [cv_dutch, cv_hungarian, cv_italian, cv_polish, cv_spanish] 
    
def get_cv_path(cv_root_folder, folder_name):
    if cv_root_folder not in cv_root_folders: return None
    if folder_name not in 'textgrid,clips,transcription'.split(','):
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
