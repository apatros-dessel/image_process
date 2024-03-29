from razmetka import *

path = r'd:\test'
txt_path = r'c:\Users\admin\Downloads\12_bit.txt'
kan_folder = r'e:\temp'

# folder_index = MaskTypeFolderIndex(path)
# folder_index.ImportQLReport(SetQlXlsPathList(path = r'\\172.21.195.2\thematic\!SPRAVKA\S3'))

with open(txt_path) as txt:
    txt_id_list = txt.read().split('\n')

# scroll(DictCounts({}, txt_id_list), counts=1)

for corner, folders, files in os.walk(r'y:\\'):
    for id in txt_id_list:
        if id in corner:
            for file in files:
                if file.lower().endswith('tif'):
                    copyfile(file, fullpath(kan_folder, file))
                    print('DONE: ' + file)
                    break

sys.exit()
for txt_id in txt_id_list:
    kan_id = txt_id.split('.MS')[0] + '.PAN.L2'
    folder_index.DownloadQL(kan_id, kan_folder, geom_path = None, ql_id = None)
    # MakeQuicklook(fullpath(kan_folder, kan_id, 'tif'), fullpath(kan_folder, kan_id + '_30m', 'tif'), epsg=None, pixelsize=30, method=gdal.GRA_Average, overwrite=False)
    # print('%s %s' % (str(os.path.exists(fullpath(kan_folder, kan_id, 'tif'))), kan_id))
    # os.rename(fullpath(kan_folder, kan_id, 'tif'), fullpath(kan_folder, txt_id, 'tif'))