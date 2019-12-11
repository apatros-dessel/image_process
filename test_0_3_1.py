from image_processor import *

path = r'c:\sadkov\playground\test\planet'

proc = process(output_path=r'c:\sadkov\playground\test')
proc.input(path)

# TEST SCENES

def print_scene(ascene):

    print('\n### SCENE DESCRIPTION ###')
    print('Image System')
    scroll(ascene.imsys)
    print('Full path')
    scroll(ascene.fullpath)
    print('Path')
    scroll(ascene.path)
    print('File path')
    scroll(ascene.filepath)
    print('Files')
    scroll(ascene.files)
    print('Clip paremeters')
    scroll(ascene.clip_parameters)

    print('\n### METADATA DESCRIPTION ###')
    print('Satellite')
    scroll(ascene.meta.sat)
    print('Container')
    scroll(ascene.meta.container)
    print('Files')
    scroll(ascene.meta.files)
    print('Filepaths')
    scroll(ascene.meta.filepaths)
    print('Bandpaths')
    scroll(ascene.meta.bandpaths)
    print('Datetime')
    scroll(ascene.meta.datetime)
    print('Namecodes')
    scroll(ascene.meta.namecodes)

    print('\n')

    return None

def make_composites_from_list(ascene, complist, folder):
    for comp_id in complist:
        filename = ascene.meta.name(r'test_0.3.1_[date]_[sat]_{}.tif'.format(comp_id))
        full = fullpath(folder, filename)
        ascene.default_composite(comp_id, full)

def count_indices_from_list(ascene, indexlist, folder):
    for index_id in indexlist:
        filename = ascene.meta.name(r'test_0.3.1_[date]_[sat]_{}.tif'.format(index_id))
        full = fullpath(folder, filename)
        ascene.calculate_index(index_id, full)

for ascene in proc.scenes:
    print_scene(ascene)
    # make_composites_from_list(ascene, ['RGB', 'NIR', 'SWIR'], proc.output_path)
    # count_indices_from_list(ascene, ['NDVI', 'NDWI', 'NDBI'], proc.output_path)
