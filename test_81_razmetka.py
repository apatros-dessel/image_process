from razmetka import *

path = r'\\172.21.195.2\thematic\!razmetka\Kanopus\Kanopus_snow'

folder_index = MaskTypeFolderIndex(path)

# scroll(folder_index.subtypes['img_cloud']['MS']['img'])

# folder_index.UpdateFromMS('PAN','img_without_clouds',use_source_pms=False)
folder_index.SaveBandsSeparated('&img_autumn')
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')