from progressbar import progressbar

longer = 'ː'

def make_bpcs():
    '''make a BPCs instance with all broad phonetic classes.'''
    names = 'plosive,nasal,approximant,fricative,affricate,voiced,voiceless'
    names += ',high,mid,low,front,central'
    names += ',back,diphtong,consonant,vowel'
    names = names.split(',')
    bpcs = 'p pʰ t tʰ k kʰ b d g ɡ' # plosive
    bpcs += ',n m ŋ ɲ ɱ' # nasal
    bpcs += ',l r j J w ʋ ʎ ɥ' # approximant
    bpcs += ',s ʃ ʒ h f x z v ɣ ð θ β ç' # fricative
    bpcs += ',tʃ ʒd ts pf'  # affricate
    bpcs += ',b d g ɡ m ɱ n ŋ ɲ l r j J w ʋ ʎ ʒ dʒ z v ð β ʀ' # voiced
    bpcs += ',p pʰ t tʰ k kʰ s ʃ tʃ h f x ɣ θ ts pf ç ɥ' # voiceless
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ' # high
    bpcs += ',ʏ ø e ẽ ɛ ɛ̃ ɔ ɔ̃ o õ ə ɜ œ ɶ̃' # mid
    bpcs += ',a ɑ ɒ ä ã ɑ̃ ɐ' # low
    bpcs += ',y i ɪ e ẽ ɛ ɛ̃ a ɶ̃' # front
    bpcs += ',œ ø ʉ ɨ ə ɜ ä ã ɐ' # central
    bpcs += ',u ʊ o õ ɔ ɔ̃ ɑ ɑ̃ ɒ' # back
    bpcs += ',ɛi œy ɑu ɔi ɔu oːi ɛɪ eːu aːi yu ui əʊ iu ɔɪ' #diphtong 
    bpcs += ' eʊ eɪ aʊ aɪ ɔʏ' # diphtong
    bpcs += ',p pʰ t tʰ k kʰ b d g ɡ n m ŋ ɲ l r j J w ʋ s ʀ' # consonant
    bpcs += ' ʃ tʃ ʒ h ts pf ç ɥ' # consonant
    bpcs += ' f x z v ɣ ð θ ʎ ɱ β' # consonant
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ ʏ ø e ẽ ɛ ɛ̃ ɔ ɔ̃ o õ ə ɜ œ a ɑ ɒ ä ã ɑ̃' # vowel
    bpcs += ' ɛi œy ɑu ɔi ɔu oːi ɛɪ eːu aːi yu ui əʊ iu ɔɪ eʊ eɪ aʊ aɪ' # vowel
    bpcs += ' ɐ ɔʏ ɶ̃' # vowel
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
    
    
    
