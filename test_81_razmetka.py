from razmetka import *

path = r'\\172.21.195.2\thematic\!razmetka\Kanopus\Kanopus_clouds'

folder_index = MaskTypeFolderIndex(path, datacat='img_check')
folder_index.FillMaskBandclasses()
# scroll(folder_index.bandclasses)
folder_index.FillMaskSubtypes(datacat='img_check')
# scroll(folder_index.subtypes)
# sys.exit()

# folder_index.UpdateFromMS('PAN','img_without_clouds',use_source_pms=False)

for subtype in folder_index.subtypes:
    folder_index.SaveBandsSeparated(subtype, datacat='img_check')
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')