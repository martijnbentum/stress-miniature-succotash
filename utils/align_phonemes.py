import needleman_wunch as nw
import ipasymbols
import gruut_ipa

vowels = ipasymbols.phonlist(query={'type':'vowel'})
vowels.append('ɔː') 
vowels.append('ɪə') 
vowels.append('ʊə') 
vowels.append('ɛə') 
vowels.append('oʊ') 
vowels.append('ɑː') 
vowels.append('əʊ') 
vowels.append('ai')
vowels.append('ei')
vowels.append('eɪ')
vowels.append('ɜː')
vowels.append('ɑɪ')
vowels.append('uː')
vowels.append('ɔɪ')
vowels.append('ɝ')
vowels.append('aʊ')
vowels.append('ɑ̃ː')
vowels.append('iː')
vowels.append('ɑu')


consonants = ipasymbols.phonlist(query={'type': ["pulmonic", "non-pulmonic"]})
consonants.append('n̩')
consonants.append('l̩')
consonants.append('tʃ')
consonants.append('dʒ')
consonants.append('g')
consonants.append('w')
consonants.append('m̩')


def align_space_separated_arpabet(celex, textgrid):
    c, tg = nw.nw(celex,textgrid).split('\n')
    return c, tg

def _has_next(index, sequence):
    return index < len(sequence) -1

def _has_previous(index, sequence = None):
    return index > 0

def get_celex_phonemes(celex_index,celex_phonemes):
    if _has_next(celex_index,celex_phonemes):
        next_pc = celex_phonemes[celex_index + 1]
    else: next_pc = None
    if _has_previous(celex_index,celex_phonemes):
        previous_pc = celex_phonemes[celex_index -1]
    else: previous_pc = None
    if celex_index < len(celex_phonemes):
        pc = celex_phonemes[celex_index]
    else: pc = None
    return previous_pc, pc, next_pc

def check_phoneme(phoneme, name):
    if phoneme in vowels or phoneme in consonants:pass
    else: raise ValueError(phoneme,name, 'not in vowels or consonants')

def _check_phonemes(textgrid_phoneme,previous_pc,next_pc):
    check_phoneme(textgrid_phoneme.ipa,'textgrid_phoneme')
    check_phoneme(previous_pc.ipa,'previous_pc')
    check_phoneme(next_pc.ipa,'next_pc')

def compute_consonant_similarity_score(c1,c2):
    if c1 == 'tʃ': c1 ='ʃ'
    if c2 == 'tʃ': c2 ='ʃ'
    c1 = gruut_ipa.constants.CONSONANTS[c1]
    c2 = gruut_ipa.constants.CONSONANTS[c2]
    score = 0
    if c1.type == c2.type: score += 1
    if c1.place == c2.place: score += 1
    if c1.voiced == c2.voiced: score += 1
    return score

def _simplify_vowel(v):
    if v not in gruut_ipa.constants.VOWELS.keys():
        if len(v) > 1:
            return _simplify_vowel(v[0])
        raise ValueError(v,'cannot simplify not in vowels')
    return v

def compute_vowel_similarity_score(v1,v2):
    v1 = _simplify_vowel(v1)
    v2 = _simplify_vowel(v2)
    v1 = gruut_ipa.constants.VOWELS[v1]
    v2 = gruut_ipa.constants.VOWELS[v2]
    score = 0
    if v1.height == v2.height: score += 1
    if v1.placement == v2.placement: score += 1
    if v1.rounded== v2.rounded: score += 1
    return score

def _handle_only_vowels(textgrid_phoneme,previous_pc,next_pc):
    score_previous = compute_vowel_similarity_score(
        textgrid_phoneme.ipa, previous_pc.ipa)
    score_next = compute_vowel_similarity_score(
        textgrid_phoneme.ipa, next_pc.ipa)
    if score_previous > score_next: return previous_pc
    return next_pc

def _handle_only_consonants(textgrid_phoneme,previous_pc,next_pc):
    score_previous = compute_consonant_similarity_score(
        textgrid_phoneme.ipa, previous_pc.ipa)
    score_next = compute_consonant_similarity_score(
        textgrid_phoneme.ipa, next_pc.ipa)
    if score_previous > score_next: return previous_pc
    return next_pc

def handle_no_celex(textgrid_phoneme,previous_pc,next_pc):
    if not next_pc: return previous_pc
    if not previous_pc: return next_pc
    _check_phonemes(textgrid_phoneme,previous_pc,next_pc)
    if previous_pc.syllable_index == next_pc.syllable_index:
        return next_pc
    if previous_pc.ipa in vowels and next_pc.ipa in vowels:
        if textgrid_phoneme.ipa in consonants:
            return next_pc
        else:
            return _handle_only_vowels(textgrid_phoneme,previous_pc,next_pc)
    if previous_pc.ipa in consonants and next_pc.ipa in consonants:
        if textgrid_phoneme.ipa in vowels: return previous_pc
        return _handle_only_consonants(textgrid_phoneme,previous_pc,next_pc)
    if previous_pc.ipa in vowels and next_pc.ipa in consonants:
        if textgrid_phoneme.ipa in vowels:
            return previous_pc
        if textgrid_phoneme.ipa in consonants:
            return next_pc
    if previous_pc.ipa in consonants and next_pc.ipa in vowels:
        if textgrid_phoneme.ipa in vowels:
            return next_pc
        if textgrid_phoneme.ipa in consonants:
            return previous_pc
    raise ValueError('not found', previous_pc.ipa,next_pc.ipa,
        textgrid_phoneme.ipa)

def check_syllable_index(word):
    if word.table.phonemes[0].syllable_index == 0: 
        word.syllable_index_fixed = False
        return word 
    for phoneme in word.table.phonemes:
        phoneme.syllable_index -= 1
    word.syllable_index_fixed = True
    return word


def set_textgrid_phonemes_syllable_index_mald(word):
    '''
    aligns the phonemes of textgrid transcription and celex transcription
    in the case that they do not have an equal number of phonemes
    uses needleman wunch to align both phoneme sequences
    than maps syllable index from the celex representation to the
    textgrid representation
    if now celex phoneme is present at the transcription phoneme
    index it compare the transcription phoneme with the preceding and
    following celex phoneme and gets the syllable index from the closest
    match
    '''
    celex = ''.join([p.phoneme for p in word.celex_word.phonemes])
    textgrid= ''.join([p.disc for p in word.table.phonemes])
    celex_phonemes = word.celex_word.phonemes
    celex_index = 0
    textgrid_index = 0
    celex,textgrid = nw.nw(celex,textgrid).split('\n')
    for c, t in zip(celex, textgrid):
        if textgrid_index >= len(word.table.phonemes): continue
        previous_pc,pc,next_pc= get_celex_phonemes(celex_index,celex_phonemes)
        textgrid_phoneme = word.table.phonemes[textgrid_index]
        if t != '-' and c != '-':
            textgrid_phoneme.syllable_index = pc.syllable_index
            textgrid_phoneme.celex_phoneme_index= pc.phoneme_index
            textgrid_index += 1
            celex_index += 1
            continue
        if t == '-':
            celex_index += 1
            continue
        if c != '-': raise ValueError(c,t, celex_index,textgrid_index)
        textgrid_index += 1
        next_pc = pc
        pc = handle_no_celex(textgrid_phoneme,previous_pc,next_pc)
        textgrid_phoneme.syllable_index = pc.syllable_index
        textgrid_phoneme.celex_phoneme_index = pc.phoneme_index
    word = check_syllable_index(word)
    return word


        
            
