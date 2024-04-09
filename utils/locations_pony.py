from pathlib import Path

#CGN root
cgn_root = Path('/vol/bigdata/corpora2/CGN2')
cgn_data = cgn_root / 'data'
cgn_audio = cgn_data / 'audio/wav'
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


