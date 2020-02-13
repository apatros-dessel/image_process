from image_processor import *
from shutil import copyfile

input_list = [
    r'f:\rks\tver',
    # r'd:\digital_earth\2018_SNT\S2A_MSIL1C_20180525T084601_N0206_R107_T37VCC_20180525T110427.SAFE',
]

output_path = r'd:\digital_earth\neuro\n2\copy_planet'

vector_cover_path = r'f:\rks\digital_earth\tver_city.shp'

proc = process(output_path=output_path)
proc.input(input_list, ['PLN'])

cover_ds, cover_lyr = geodata.get_lyr_by_path(vector_cover_path)
feat = cover_lyr.GetNextFeature()
geom = feat.GetGeometryRef()
geom = geodata.ogr.Geometry(wkt=geom.ExportToWkt())

# print(cover_lyr.GetExtent())
# print(geom.ExportToWkt())

scene_dict = OrderedDict()

for ascene in proc.scenes:
    scene_ds, scene_lyr = geodata.get_lyr_by_path(fullpath(ascene.path, ascene.meta.datamask))
    # print(scene_lyr.GetExtent())
    scene_feat = scene_lyr.GetNextFeature()
    scene_geom = scene_feat.GetGeometryRef()
    scene_geom = geodata.ogr.Geometry(wkt=scene_geom.ExportToWkt())
    # print(scene_geom.ExportToWkt())
    # print(scene_geom.Intersection(geom).ExportToWkt())
    if scene_geom.Intersects(geom):
        scene_dict[ascene.meta.id] = ascene.path

# print(geom.ExportToWkt())

scroll(scene_dict)

for sceneid in scene_dict:
    scene_path = scene_dict[sceneid]
    scene_folder = os.path.basename(scene_path)
    scene_folder_path = fullpath(output_path, scene_folder)
    if not os.path.exists(scene_folder_path):
        os.makedirs(scene_folder_path)
    for filename in os.listdir(scene_path):
        copyfile(fullpath(scene_path, filename), fullpath(scene_folder_path, filename))


