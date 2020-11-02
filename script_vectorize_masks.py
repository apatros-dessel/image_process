from geodata import *

path = r'e:\test\razmetka\data\db_etalons'
folders = folder_paths(path)[0][7:21]

scroll(folders)

for folder in folders:

    fmsk = fullpath(folder, 'masks')
    fshp = fullpath(folder, 'shp')

    if os.path.exists(fmsk) and os.path.exists(fshp):

        for msk in folder_paths(fmsk,1,'tif'):

            f,n,e = split3(msk)
            VectorizeBand((msk,1), fullpath(fshp,n,'shp'), classify_table=None, index_id='GRIDCODE', overwrite=False)
