from utils import needleman_wunch as nw
import gruut_ipa
import ipasymbols
import json

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


def align_celex_maus_ipa(celex_word, maus_word):
    celex_ipa = [x[0] for x in celex_word.ipa.split(' ')]
    word_ipa = [x[0] for x in maus_word.ipa.split(' ')]
    celex_ipa, word_ipa = nw.nw(celex_ipa,word_ipa).split('\n')
    return celex_ipa, word_ipa

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

def _handle_only_vowels(word_phoneme,previous_pc,next_pc):
    score_previous = compute_vowel_similarity_score(
        word_phoneme.ipa, previous_pc.ipa)
    score_next = compute_vowel_similarity_score(
        word_phoneme.ipa, next_pc.ipa)
    if score_previous > score_next: return previous_pc
    return next_pc

def _handle_only_consonants(word_phoneme,previous_pc,next_pc):
    score_previous = compute_consonant_similarity_score(
        word_phoneme.ipa, previous_pc.ipa)
    score_next = compute_consonant_similarity_score(
        word_phoneme.ipa, next_pc.ipa)
    if score_previous > score_next: return previous_pc
    return next_pc

def handle_no_celex(word_phoneme,previous_pc,next_pc):
    if not next_pc: return previous_pc
    if not previous_pc: return next_pc
    _check_phonemes(word_phoneme,previous_pc,next_pc)
    if previous_pc.syllable_index == next_pc.syllable_index:
        return next_pc
    if previous_pc.ipa in vowels and next_pc.ipa in vowels:
        if word_phoneme.ipa in consonants:
            return next_pc
        else:
            return _handle_only_vowels(word_phoneme,previous_pc,next_pc)
    if previous_pc.ipa in consonants and next_pc.ipa in consonants:
        if word_phoneme.ipa in vowels: return previous_pc
        return _handle_only_consonants(word_phoneme,previous_pc,next_pc)
    if previous_pc.ipa in vowels and next_pc.ipa in consonants:
        if word_phoneme.ipa in vowels:
            return previous_pc
        if word_phoneme.ipa in consonants:
            return next_pc
    if previous_pc.ipa in consonants and next_pc.ipa in vowels:
        if word_phoneme.ipa in vowels:
            return next_pc
        if word_phoneme.ipa in consonants:
            return previous_pc
    raise ValueError('not found', previous_pc.ipa,next_pc.ipa,
        word_phoneme.ipa)

def check_syllable_index(word):
    if word.table.phonemes[0].syllable_index == 0: 
        word.syllable_index_fixed = False
        return word 
    for phoneme in word.table.phonemes:
        phoneme.syllable_index -= 1
    word.syllable_index_fixed = True
    return word

def _set_phoneme_stress(phoneme, stress):
    phoneme.stress = stress
    phoneme.save()

def _set_syllable_stress(word, stressed_syllable_id,unstressed_syllable_ids):
    syllables = word.syllable_set.all()
    for syllable in syllables:
        if syllable.id == stressed_syllable_id:
            syllable.stress = True
        elif syllable.id in unstressed_syllable_ids:
            syllable.stress = False
        else: raise ValueError('no stress', syllable.id, stressed_syllable_id,
            unstressed_syllable_ids)
        syllable.save()

        
def set_syllable_stress(word, word_phonemes, celex_word):
    stress_syllable_id= list(set([x.syllable_id for x in word_phonemes 
        if x.stress]))
    stressed_syllable_ids = []
    unstressed_syllable_ids = []
    for phoneme in word_phonemes:
        if phoneme.stress:
            if phoneme.syllable_id not in stressed_syllable_ids:
                stressed_syllable_ids.append(phoneme.syllable_id)
        elif phoneme.stress == False:
            if phoneme.syllable_id not in unstressed_syllable_ids:
                unstressed_syllable_ids.append(phoneme.syllable_id)
        else: raise ValueError('no stress',phoneme.stress, 
            phoneme,phoneme.identifier)
    if len(stress_syllable_id) ==  1:
        stress_syllable_id = stressed_syllable_ids
            
    

    print(stress_syllable_indices)
    return word

def add_celex_to_word(word, celex_word):
    info = json.loads(word.info)
    info['celex'] = celex_word.line
    word.info = json.dumps(info)
    word.save()



def set_lexical_stress(word, celex_database= None):
    '''
    aligns the phonemes of maus FA word and celex transcription
    in the case that they do not have an equal number of phonemes
    uses needleman wunch to align both phoneme sequences
    than maps the stress from the celex representation to the
    maus FA word representation
    if no celex phoneme is present at the transcription phoneme
    index it compares the transcription phoneme with the preceding and
    following celex phoneme and gets the stress from the closest
    match
    '''
    if not celex_database: celex_database=celex.Celex(word.language.language)
    celex_word = celex_database.get_word(word.word)
    if not celex_word: return None 
    celex_index = 0
    word_index = 0
    celex_ipa,word_ipa= align_celex_maus_ipa(celex_word,word)
    celex_phonemes = celex_word.phonemes
    word_phonemes = word.phoneme_set.all()
    for c, w in zip(celex_ipa, word_ipa):
        if word_index >= len(word_phonemes): continue
        previous_pc,pc,next_pc= get_celex_phonemes(celex_index,celex_phonemes)
        word_phoneme = word_phonemes[word_index]
        print(c,w,word_phoneme,pc, word_index, celex_index)
        if w != '-' and c != '-':
            _set_phoneme_stress(word_phoneme, pc.stressed)
            word_index += 1
            celex_index += 1
            continue
        if w == '-':
            celex_index += 1
            continue
        if c != '-': raise ValueError(c,w, celex_index,word_index)
        word_index += 1
        next_pc = pc
        pc = handle_no_celex(word_phoneme,previous_pc,next_pc)
        syllable_index = pc.syllable_index
        if celex_word.stress_list[syllable_index] == 'primary': stress = True
        else: False
        _set_phoneme_stress(word_phoneme, stress)
    _set_syllable_stress(word, word_phonemes, celex_word)
    add_celex_to_word(word, celex_word)
    return word


        
            
