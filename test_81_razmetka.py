from razmetka import *

path = r'\\172.21.195.2\thematic\!razmetka\Meteor_MSU'
datacat = 'img'

folder_index = MaskTypeFolderIndex(path, datacats=datacat)
folder_index.FillMaskBandclasses()
# scroll(folder_index.bandclasses)
folder_index.FillMaskSubtypes(datacats=datacat)
# scroll(folder_index.subtypes)
# sys.exit()

# folder_index.VectorizeRasterMasks(bandclass='MS', subtype='strips', datacat='shp_auto', replace={0:255}, delete_vals=0)
# folder_index.UpdateFromMS('PAN','img_mist_cloud_shadow_surface',use_source_pms=False)
folder_index.SaveBandsSeparated('total', datacat='img', satellite='Meteor')
sys.exit()
for subtype in folder_index.subtypes.keys():
    # print(folder_index.Subtype(subtype))
    # folder_index.UpdateFromMS('PMS', subtype, use_source_pms=False)
    folder_index.SaveBandsSeparated(subtype, datacat=datacat)
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')