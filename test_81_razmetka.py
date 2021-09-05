from razmetka import *

path = r'\\172.21.195.2\thematic\!razmetka\Resurs_KSHMSA\Resurs_KSHMSA_CP\Resurs_KSHMSA_CP_surface'
datacat = 'img_check'

folder_index = MaskTypeFolderIndex(path, datacats=datacat)
folder_index.FillMaskBandclasses()
scroll(folder_index.bandclasses)
folder_index.FillMaskSubtypes(datacats=datacat)
scroll(folder_index.subtypes.keys())
# folder_index.UpdateFolderTif(r'e:\rks\source\Ресурс_КШМСА')
folder_index.ImportQLReport(SetQlXlsPathList(path = r'\\172.21.195.2\thematic\!SPRAVKA\S3'))
# sys.exit()

# indices = ['surface_cloud_originals', '&without_cloud_originals']
indices = ['']#'cloud_originals', 'surface_original']
# indices = ['&full_cloud', '&autumn_original', '&without_cloud_originals', 'less_snow_original', 'mist_coeff_original', 'surface_cloud_originals', 'thick_snow_original', 'water_originals']
# indices = ['&full_cloud', '&autumn_cut', '&without_cloud_cut', 'less_snow_cut', 'mist_coeff_original',
# 'surface_cloud_cut', 'thick_snow_cut', 'water_cut']

# folder_index.VectorizeRasterMasks(bandclass='MS', subtype='strips', datacat='shp_auto', replace={0:255}, delete_vals=0)
# folder_index.UpdateFromMS('PAN','surface_cloud_originals',use_source_pms=False)
# folder_index.SaveBandsSeparated('clouds_surface', datacat='img', satellite='Kanopus')
# folder_index.CreateQuicklookSubtype(30, bandclass='PMS', subtype='', datacat=datacat, satellite='Kanopus')
# sys.exit()
# os.system('python3 test_16_clip_raster.py')
for subtype in indices:
    # print(folder_index.Subtype(subtype))
    # folder_index.UpdateFromMS('PMS', subtype, use_source_pms=False, datacat=datacat)
    # folder_index.CreateQuicklookSubtype(30, bandclass='PAN', subtype=subtype, datacat=datacat, satellite='Resurs')
    folder_index.SaveBandsSeparated(subtype, datacat=datacat, satellite='KSHMSA-SR')
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')