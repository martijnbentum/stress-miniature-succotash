from utils import needleman_wunch as nw
import gruut_ipa
from itertools import product
import json
from load import load_bpc
import unicodedata

def is_vowel(ipa, d = None):
    if not d: d = load_bpc.ipa_to_bpc_dict()
    if hasattr(ipa, 'ipa'): ipa = ipa.ipa
    return load_bpc.is_vowel(ipa, d)

def is_consonant(ipa, d = None):
    if not d: d = load_bpc.ipa_to_bpc_dict()
    if hasattr(ipa, 'ipa'): ipa = ipa.ipa
    return load_bpc.is_consonant(ipa, d)

def compute_similarity_score_word_celex(phonemes):
    score = 0
    for word_phoneme in phonemes:
        celex_phoneme = word_phoneme.celex_phoneme
        score += compute_similarity_score_phoneme_pair(word_phoneme, 
            celex_phoneme)
    return score / len(phonemes)

def compute_similarity_score_phoneme_pair(p1 , p2):
    if not p1: return 0
    if not p2: return 0
    if hasattr(p1,'ipa'): p1 = p1.ipa
    if hasattr(p2,'ipa'): p2 = p2.ipa
    p1 = simplify_phoneme(p1)
    p2 = simplify_phoneme(p2)
    p1_is_vowel = is_vowel(p1)
    p2_is_vowel = is_vowel(p2)
    if p1_is_vowel != p2_is_vowel: 
        return -1
    if not p1 or not p2: return -1
    if p1_is_vowel and p2_is_vowel: 
        return compute_vowel_similarity_score(p1, p2)/3
    if not p1_is_vowel and not p2_is_vowel: 
        return compute_consonant_similarity_score(p1, p2)/3
    raise ValueError('case should not occur', p1, p2, p1_is_vowel, p2_is_vowel)
    

def _handle_long_phoneme(p1,p2, f):
    score = 0
    phoneme_pairs = list(set(product(p1,p2)))
    phoneme_pairs = _remove_diacritics(phoneme_pairs)
    for p1,p2 in phoneme_pairs:
        score += f(p1,p2)
    return score / len(phoneme_pairs)


def remove_diacritics(text):
    normalized_text = unicodedata.normalize('NFD', text)
    cleaned_text = ''.join(c for c in normalized_text 
        if unicodedata.category(c) != 'Mn')
    return cleaned_text

def simplify_phoneme(phoneme):
    for char in 'ʰʲː':
        phoneme = phoneme.replace(char,'')
    phoneme = remove_diacritics(phoneme)
    return phoneme

def compute_consonant_similarity_score(c1,c2):
    c1 = simplify_phoneme(c1)
    c2 = simplify_phoneme(c2)
    k = gruut_ipa.constants.CONSONANTS.keys()
    if c1 not in k or c2 not in k:
        if len(c1) > 1 or len(c2) > 1:
            return _handle_long_phoneme(c1,c2,
                compute_consonant_similarity_score)
        else: 
            m = 'c status: ' +c1 +' '+ str(c1 in k)+', '+c2+' '+ str(c2 in k)
            raise ValueError(m)
    c1 = gruut_ipa.constants.CONSONANTS[c1]
    c2 = gruut_ipa.constants.CONSONANTS[c2]
    score = 0
    if c1.type == c2.type: score += 1
    if c1.place == c2.place: score += 1
    if c1.voiced == c2.voiced: score += 1
    return score

def compute_vowel_similarity_score(v1,v2):
    v1 = simplify_phoneme(v1)
    v2 = simplify_phoneme(v2)
    k = gruut_ipa.constants.VOWELS.keys()
    if v1 not in k or v2 not in k:
        if len(v1) > 1 or len(v2) > 1:
            return _handle_long_phoneme(v1, v2,
                compute_vowel_similarity_score)
        else:
            m='vowel status: ' + v1 +' '+ str(v1 in k)+', '+v2+' '+ str(v2 in k)
            raise ValueError(m)
    v1 = gruut_ipa.constants.VOWELS[v1]
    v2 = gruut_ipa.constants.VOWELS[v2]
    score = 0
    if v1.height == v2.height: score += 1
    if v1.placement == v2.placement: score += 1
    if v1.rounded== v2.rounded: score += 1
    return score

diacritics = ['͂','̩','̃']
