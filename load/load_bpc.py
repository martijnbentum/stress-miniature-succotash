from progressbar import progressbar

longer = 'ː'

def make_bpcs():
    '''make a BPCs instance with all broad phonetic classes.'''
    names = 'plosive,nasal,approximant,fricative,affricate,voiced,voiceless'
    names += ',high,mid,low,front,central'
    names += ',back,diphtong,consonant,vowel'
    names = names.split(',')
    bpcs = 'p pʰ t tʰ tːʲ tʲ k kʰ b d dʲ dːʲ g ɡ c pʲ kʲ ɡʲ ʔ' # plosive
    bpcs += ',n m ŋ ɲ ɱ nʲ ŋ̩ n̩ m̩' # nasal
    bpcs += ',l r j J w ʋ ʎ ɥ l̩ ɹ' # approximant
    bpcs += ',s ʃ ʒ h f x z v ɣ ð θ β ç zʲ xʲ sʲ ɦ ʍ' # fricative
    bpcs += ',tʃ ʒd ts pf tːʃ tːs dːz dz dːʒ tsʲ dzʲ dʒ'  # affricate
    bpcs += ',b d dʲ dːʲ g ɡ m ɱ n ŋ ɲ l r j J w ʋ ʎ ʒ dʒ z v ð β ʀ' # voiced
    bpcs += ' dːz dz dːʒ dzʲ zʲ nʲ ɡʲ ŋ̩ n̩ m̩ l̩ ɦ ɾ ɹ ʒd' # voiced
    bpcs += ',p pʰ t tʰ tːʲ k kʰ s ʃ tʃ h f x ɣ θ ts pf ç ɥ ʔ' # voiceless
    bpcs += ' tːʃ tːs tʲ c tsʲ xʲ sʲ pʲ kʲ ʍ' # voiceless
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ' # high
    bpcs += ',ʏ ø e ẽ ɛ ɛ̃ ɔ ɔ̃ o õ ə ɜ œ ɶ̃ ɝ ʌ ə͂' # mid
    bpcs += ',a ɑ ɒ ä ã ɑ̃ ɐ æ̃ æ' # low
    bpcs += ',y i ɪ e ẽ ɛ ɛ̃ a ɶ̃ æ̃ æ' # front
    bpcs += ',œ ø ʉ ɨ ə ɜ ä ã ɐ ɝ ə͂' # central
    bpcs += ',u ʊ o õ ɔ ɔ̃ ɑ ɑ̃ ɒ ʌ' # back
    bpcs += ',ɛi œy ɑu ɔi ɔu oːi ɛɪ eːu aːi yu ui əʊ iu ɔɪ' #diphtong 
    bpcs += ' eʊ eɪ aʊ aɪ ɔʏ ei ʊə ɪə eə iːə oɪ æɔ æɪ ɑe əʉ' # diphtong
    bpcs += ' ɪiː ʌʊ ʌi ʊʉ ɒɪ æo ɔe oe ae ʌʉ iə ɔɛ ʌə ɔə oə ɛə' # diphtong
    bpcs += ',p pʰ t tʰ tːʲ k kʰ b d dːʲ g ɡ n m ŋ ɲ l r j J w ʋ s ʀ' #consonant
    bpcs += ' ʃ tʃ ʒ h ts pf ç ɥ tːʃ tːs tʲ dʲ dːz dz dːʒ ʔ n̩ m̩' # consonant
    bpcs += ' f x z v ɣ ð θ ʎ ɱ β c tsʲ dzʲ zʲ xʲ sʲ pʲ nʲ kʲ ɡʲ ŋ̩' # consonant
    bpcs += ' l̩ ɦ ɾ ɹ ʍ dʒ ʒd' # consonant
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ ʏ ø e ẽ ɛ ɛ̃ ɔ ɔ̃ o õ ə ɜ œ a ɑ ɒ ä ã ɑ̃' # vowel
    bpcs += ' ɛi œy ɑu ɔi ɔu oːi ɛɪ eːu aːi yu ui əʊ iu ɔɪ eʊ eɪ aʊ aɪ' # vowel
    bpcs += ' ɐ ɔʏ ɶ̃ æ̃ ei ʊə ɪə eə ɝ ʌ æ iːə oɪ æɔ æɪ ɑe əʉ ɛə' # vowel
    bpcs += ' ɪiː ʌʊ ʌi ʊʉ ɒɪ æo ɔe oe ae ʌʉ iə ə͂ ɔɛ ʌə ɛə ɔə oə' # vowel
    bpcs = [x.split() for x in bpcs.split(',')]
    return dict(zip(names,bpcs))

def ipa_to_bpc_dict(add_longer=False):
    '''return the broad phonetic class of a given IPA symbol.'''
    d = {}
    bpcs = make_bpcs()
    ipas = []
    vowels = bpcs['vowel']
    for phonemes in bpcs.values():
        ipas.extend(phonemes)
    for ipa in ipas:
        for bpc, phonemes in bpcs.items():
            if not ipa in d.keys(): d[ipa] = []
            if ipa in phonemes and bpc not in d[ipa]: d[ipa].append( bpc ) 
            if ipa + longer not in d.keys(): d[ipa + longer] = []
            if ipa in phonemes and bpc not in d[ipa + longer]: 
                d[ipa + longer].append( bpc ) 
    return d

def ipa_to_bpc_instances(add_longer=False):
    from text.models import BPC
    d = ipa_to_bpc_dict()
    output = {}
    for ipa, bpcs in d.items():
        output[ipa] = BPC.objects.filter(bpc__in=bpcs)
    return output

def handle_bpc(bpc, bpcs):
    from text.models import BPC
    d = {}
    d['bpc'] = bpc
    d['ipa'] = bpcs[bpc]
    _, created = BPC.objects.get_or_create(**d)
    return created

def handle_bpcs():
    bpcs = make_bpcs()
    for bpc in progressbar(bpcs.keys()):
        handle_bpc(bpc, bpcs)

def get_consonants(d=None):
    if not d: d = ipa_to_bpc_dict()
    consonants = [c for c,bpc in d.items() if 'consonant' in bpc]
    consonants.append('*') # add celex consonant (specific r in english)
    return consonants

def get_vowels(d=None):
    if not d: d = ipa_to_bpc_dict()
    vowels = [vowel for vowel,bpc in d.items() if 'vowel' in bpc]
    celex_vowels = 'œ̃ au ɔy ai ɑɪ yːː iːː'.split(' ')# celex vowels
    vowels.extend(celex_vowels)
    return vowels
    
def is_vowel(ipa, d=None):
    '''return True if the given IPA symbol is a vowel.'''
    vowels = get_vowels(d)
    return ipa in vowels

def is_consonant(ipa, d=None):
    '''return True if the given IPA symbol is a consonant.'''
    consonants = get_consonants(d)
    return ipa in consonants
    
def handle_phoneme(phoneme, skip_based_bpcs_str = True):
    '''if phoneme does not have bpc this function will add it'''
    if phoneme.bpcs_str and skip_based_bpcs_str: return
    ipa_to_bpc = ipa_to_bpc_instances(add_longer=True)
    bpcs = ipa_to_bpc[phoneme.ipa]
    phoneme.bpcs_str = ','.join([bpc.bpc for bpc in bpcs])
    phoneme.save()
    phoneme.bpcs.add(*bpcs)

def handle_language(language_name, skip_based_bpcs_str = True):
    '''add bpcs to all phonemes of a given language.'''
    from text.models import Language, Phoneme
    language = Language.objects.get(language__iexact=language_name)
    phonemes = Phoneme.objects.filter(language=language)
    for phoneme in progressbar(phonemes):
        handle_phoneme(phoneme, skip_based_bpcs_str)

def group_phonemes(ipa_list, groups = ''):
    if not groups:
        groups = 'plosive,nasal,approximant,fricative'
        groups += ',high,mid,low,diphtong'
        groups = groups.split(',')
    bpc = ipa_to_bpc_dict()
    group_dict = {group:[] for group in groups}
    used, double = [], []
    for group in group_dict.keys():
        for ipa in ipa_list:
            names = bpc[ipa]
            if group in names:
                if ipa not in used: 
                    used.append(ipa)
                    group_dict[group].append(ipa)
                else:
                    double.append([ipa,group])
    grouped_list = []
    for group in groups:
        grouped_list.extend(group_dict[group])
    print('double:', double)
    return grouped_list, group_dict, double
    
    
