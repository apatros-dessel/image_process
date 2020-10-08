from geodata import *

pin = r'i:\Resurs_Krym'
pout = r'e:\rks\resurs_crimea'
resursp_channels = {
    '21': 'RED',
    '22': 'NIR',
    '23': 'GREEN',
    '33': 'BLUE',
}

files = folder_paths(pin,1,'tiff')

def parse_stinky_resursp(name):
    parts = name.split('_')
    if len(parts)==9:
        type = 'PAN'
        # channel = 'PAN'
    else:
        type = 'MS'
    id = '_'.join(parts[1:8])
    level = parts[7]
    channel = globals()['resursp_channels'].get(parts[-1], 'PAN')
    return id, level, type, channel

shooting_list = OrderedDict()

for file in files:
    f,n,e = split3(file)
    id, level, type, channel = parse_stinky_resursp(n)
    if id in shooting_list:
        shooting_list[id][channel] = file
    else:
        shooting_list[id] = {channel: file}

# scroll(shooting_list)

for id in shooting_list:
    channels = shooting_list[id]
    scroll(channels, header=id, lower='\n')
    bandpath = [
        (channels['RED'], 1),
        (channels['GREEN'], 1),
        (channels['BLUE'], 1),
        (channels['NIR'], 1)
    ]
    export_path = fullpath(pout, id, 'tif')
    Composite(export_path, bandpath=bandpath, rasterpath=None, band_order=None, epsg=None, compress='DEFLATE', overwrite=False)