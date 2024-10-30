def load_mondegreen_dataset(return_dict=True):
    with open('../mondegreen/MondegreensFrench_utf8.txt') as f:
        t = f.read().split('\n')
        t = [x.split('\t') for x in t]
    header = t[0]
    data = t[1:]
    header[-2:] = ['chain','transfer']
    if return_dict:
        data = [{header[i]:x[i] for i in range(len(x))} for x in data]
    return header, data

def make_artist_song_list():
    header, data = load_mondegreen_dataset()
    temp = [(x['Interpret'], x['Songtitel']) for x in data]
    artist_song = []
    for x in temp:
        if x not in artist_song:
            artist_song.append(x)
    return artist_song


