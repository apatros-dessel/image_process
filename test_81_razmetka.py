from razmetka import *

path = r'e:\rks\kantest'

folder_index = MaskTypeFolderIndex(path)

# scroll(folder_index.subtypes['img_cloud']['MS']['img'])

folder_index.UpdateFromMS('PMS','img_cloud_mist_shadow',use_source_pms=False)