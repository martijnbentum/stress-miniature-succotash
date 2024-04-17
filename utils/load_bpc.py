from progressbar import progressbar

longer = 'ː'

def make_bpcs():
    '''make a BPCs instance with all broad phonetic classes.'''
    names = 'plosive,nasal,approximant,fricative,voiced,voiceless'
    names += ',high,mid,low,front,central'
    names += ',back,diphtong,consonant,vowel'
    names = names.split(',')
    bpcs = 'p t k b d g,n m ŋ ɲ,l r j w ʋ,s ʃ ʒ h f x z v ɣ'
    bpcs += ',b d g m n ŋ ɲ l r j w ʋ ʒ z v'
    bpcs += ',p t k s ʃ h f x ɣ' 
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ'
    bpcs += ',ʏ ø e ɛ ɔ o ə ɜ œ'
    bpcs += ',a ɑ ɒ ä'
    bpcs += ',y i ɪ e ɛ a'
    bpcs += ',œ ø ʉ ɨ ə ɜ ä'
    bpcs += ',u ʊ o ɔ ɑ ɒ'
    bpcs += ',ɛi œy ɑu ɔi ɔu'
    bpcs += ',p t k b d g n m ŋ ɲ l r j w ʋ s ʃ ʒ h'
    bpcs += ' f x z v ɣ'
    bpcs += ',i ɨ ɪ y ʏ u ʉ ʊ ʏ ø e ɛ ɔ o ə ɜ œ a ɑ ɒ ä'
    bpcs += ' ɛi œy ɑu ɔi ɔu'
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
            if ipa in vowels:
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
    
    
    