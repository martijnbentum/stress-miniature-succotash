import subprocess

def soxi_info(filename):
    o = subprocess.run(['sox','--i',filename],stdout=subprocess.PIPE)
    return o.stdout.decode('utf-8')

def clock_to_duration_in_seconds(t):
    hours, minutes, seconds = t.split(':')
    s = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return s

def soxinfo_to_dict(soxinfo):
    x = soxinfo.split('\n')
    d = {}
    d['filename'] = x[1].split(': ')[-1].strip("'")
    d['n_channels'] = int(x[2].split(': ')[-1])
    d['sample_rate'] = int(x[3].split(': ')[-1])
    t = x[5].split(': ')[-1].split(' =')[0]
    d['duration'] = clock_to_duration_in_seconds(t)
    return d
