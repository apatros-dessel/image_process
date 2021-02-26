from razmetka import *

path = r'e:\rks\rsp_test\Resurs_geoton_clouds'

folder_index = MaskTypeFolderIndex(path)

# scroll(folder_index.subtypes['img_cloud']['MS']['img'])

# folder_index.UpdateFromMS('PMS','img_cloud_mist_shadow',use_source_pms=False)
folder_index.SaveBandsSeparated()
# folder_index.ReprojectPanToMs(r'e:\rks\kantest2\img_cloud_mist_shadow', 'img_cloud_mist_shadow')