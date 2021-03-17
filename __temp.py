from geodata import *

path = r'e:\rks\razmetka_source\dgready'
folders = folder_paths(path)[0][1:]

for folder in folders:
    tifs = folder_paths(folder,1,'tif')
    if len(tifs)==1:
        tif = tifs[0]
        name = split3(tif)[1]
        files = folder_paths(folder,1)
        for file in files:
            if file!=tif:
                f,n,e = split3(file)
                end_file = fullpath(f,name,e)
                print(file, end_file)
                os.rename(file, end_file)
