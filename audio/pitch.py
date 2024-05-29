from audio import audio
import json
import librosa
import numpy as np

def signal_to_pitch(signal, sr):
    f0 = librosa.yin(signal, fmin = 65, fmax=600, sr=sr)
    return [round(x) for x in f0]

def handle_phoneme(phoneme, signal, sr, save = True):
    '''compute the pitch of a phoneme object'''
    signal = audio.item_to_samples(phoneme, signal, sr)
    f0 = signal_to_pitch(signal, sr)
    phoneme._f0 = json.dumps(f0)
    if save: phoneme.save()
    return f0

def handle_word(word, signal, sr, save = True):
    '''compute the pitch of a word object'''
    phonemes = word.phoneme_set.all()
    pitches = []
    for phoneme in phonemes:
        f0 = handle_phoneme(phoneme, signal, sr)
        pitches.append(f0)
    return pitches

def handle_audio(audio):
    '''compute the pitch of all phonemes in an audio object'''
    signal, sr = audio.load_audio()
    words = audio.word_set.all()
    pitches = []
    for word in words:
        o = handle_word(word, signal, sr)
        pitches.append(o)
    return pitches

