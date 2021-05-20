from razmetka import *

path = r'\\172.21.195.2\THEMATIC\!razmetka\Resurs_geoton\Resurs_geoton_snow'
datacats = ['img', 'img_check', 'shp_hand', 'shp_auto', 'mask']

folder_index = MaskTypeFolderIndex(path, datacats=datacats)
#scroll(folder_index.bandclasses, header='bandclasses', lower = '\n')
#scroll(folder_index.subtypes, header='subtypes', lower = '\n')
# scroll(folder_index.Images(subtype='', bandclass='MS', datacat='img'))

# folder_index.UpdateFromMS('PAN','img_mist_cloud_shadow_surface',use_source_pms=False)
# sys.exit()
for subtype in folder_index.subtypes:
    # print(subtype, CorrectFolderName(subtype, ['img', 'shp_hand', 'shp_auto', 'mask']))
    folder_index.UpdateFromMS('PMS', subtype, use_source_pms=False)
    # folder_index.SaveBandsSeparated(subtype, datacat=datacat)
    # print(subtype, ' : ', folder_index.Images(subtype=subtype, bandclass='BANDS', datacat='img'))
    pass
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')