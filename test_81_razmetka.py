from razmetka import *

path = r'e:\rks\!razmetka\Resurs_KSHMSA_BP\Resurs_KSHMSA_BP_clouds'
datacat = 'img'

folder_index = MaskTypeFolderIndex(path, datacats=datacat)
folder_index.FillMaskBandclasses()
# scroll(folder_index.bandclasses)
folder_index.FillMaskSubtypes(datacats=datacat)
scroll(folder_index.subtypes)
# sys.exit()

# folder_index.VectorizeRasterMasks(bandclass='MS', subtype='strips', datacat='shp_auto', replace={0:255}, delete_vals=0)
# folder_index.UpdateFromMS('PAN','img_mist_cloud_shadow_surface',use_source_pms=False)
folder_index.SaveBandsSeparated('clouds_vr', datacat=datacat, satellite='KSHMSA-VR')
sys.exit()
for subtype in folder_index.subtypes.keys():
    # print(folder_index.Subtype(subtype))
    # folder_index.UpdateFromMS('PMS', subtype, use_source_pms=False)
    folder_index.SaveBandsSeparated(subtype, datacat=datacat)
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')