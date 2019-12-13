from image_processor import *
from shutil import copyfile

path = r'C:\source\planet'
pathlist = [

]

path2raster = r'C:/sadkov/planet_tverskaya/composite/spring/Tver_20190428_083154_1008_RGB_LERC_DEFLATE.tif'
path2mask = r'C:\sadkov\playground\test/Tver_20190428_083154_1008_CLOUDS!.tif'
path2shp = r'C:\sadkov\playground\test/Tver_20190428_083154_1008_CLOUDS.shp'

geodata.vector_mask(path2raster, path2mask, path2shp, [None, 5900, 7000], '>', nodata=0)

# proc = process(output_path=r'C:\sadkov\planet_tverskaya\borders\spring')
# proc.input(path)

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

def make_composites_from_list(ascene, complist, folder, compress = None, overwrite = True):
    for comp_id in complist:
        filename = ascene.meta.name(r'Tver_[id]_{}_LERC_DEFLATE.tif'.format(comp_id))
        full = fullpath(folder, filename)
        res = ascene.default_composite(comp_id, full, compress = compress, overwrite = overwrite)
    return res

def count_indices_from_list(ascene, indexlist, folder, compress = None):
    for index_id in indexlist:
        filename = ascene.meta.name(r'test_0.3.1_[datetime]_[sat]_{}_LERC_DEFLATE.tif'.format(index_id))
        full = fullpath(folder, filename)
        ascene.calculate_index(index_id, full, compress = compress)

# path2vector_list = []

t = datetime.now()
#report = OrderedDict()
#for ascene in proc.scenes:
    #t2 = datetime.now()
    # print(ascene.meta.datamask)
    # path2vector_list.append(fullpath(ascene.path, ascene.meta.datamask))
    # print_scene(ascene)
    # res = make_composites_from_list(ascene, ['NIR', 'RGB'], r'C:\sadkov\planet_tverskaya\composite\spring', compress = 'LERC_DEFLATE', overwrite=False)
    # count_indices_from_list(ascene, ['NDVI', 'NDWI', 'NDBI'], proc.output_path)
    # copyfile(fullpath(ascene.path, ascene.meta.datamask), fullpath(proc.output_path, ascene.meta.name('test_0.3.1_mask_[date]_[sat].json')))
    # t2 = datetime.now() - t2
    # if res == 0:
        # print('Time to save: {}'.format(t2))
    # rep_row = OrderedDict()
    # rep_row['time'] = str(t2)
    # rep_row['result'] = ['Success', 'Failure'][res]

    # report[ascene.meta.id] = rep_row



print('Total time = {}'.format(datetime.now()-t))

# try:
    # dict_to_xls(r'C:\sadkov\planet_tverskaya\composite\spring\test_report.xls', report)
# except:
    # print('Unable to export data as xls')
    # scroll(report)

# geodata.unite_vector(path2vector_list, fullpath(proc.output_path, 'test_unite_with_attr.shp'))

# print(len(proc))
