from geodata import *

path_in = r'j:\rks\rosreestr\cadastre_uchastok.json.geojson'
path_out = r'j:\rks\rosreestr\cadastre_uchastok_moscow+obl.json'

def coder(code):
    fin = code.split(':')[0]
    if len(fin) in (2,3):
        try:
            return int(fin)
        except:
            return(0)
    return 0

filter_dataset_by_col(path_in, 'cadn', [50, 77], path_out=path_out, function=coder)