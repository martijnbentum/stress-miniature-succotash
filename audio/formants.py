from pathlib import Path
from utils import locations

def audio_filename_to_formant_filename(audio):
    formant_directory = locations.formants_dir.resolve()
    name = Path(audio.filename).stem + '.formants'
    filename = formant_directory / name
    return filename

def audio_praat_cmd(audio):
    formant_filename = audio_filename_to_formant_filename(audio)
    audio_filename = Path(audio.filename).resolve()
    name = audio_filename.stem
    cmd = []
    cmd.append('Read from file: "{}"'.format(audio_filename))
    cmd.append('To Formant (burg): 0, 5, 5500, 0.025, 50')
    cmd.append('Down to Table: "no", "yes", 6, "no", 3, "yes", 3, "yes"')
    cmd.append('Save as tab-separated file: "{}"'.format(formant_filename))
    cmd.append('selectObject: "Sound {}"'.format(name))
    cmd.append('plusObject: "Formant {}"'.format(name))
    cmd.append('plusObject: "Table {}"'.format(name))
    cmd.append('Remove')
    return '\n'.join(cmd)
