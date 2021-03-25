from geodata import *

shpfiles = folder_paths(r'e:\rks\rucode\mosaics\source2\source',1,'shp')
tiffiles = folder_paths(r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\composits\8_ch',1,'tif')
pout = r'e:\rks\rucode\mosaics\source2\source'
imgfolderlist = [
    r'e:\rks\source\kanopus_test\Rucode\reproject',
    r'e:\rks\rucode\rep',
    r'e:\rks\rucode\new2\reproject',
    r'e:\rks\rucode\new3\reproject',
    r'\\172.21.195.2\thematic\Sadkov_SA\rucode\reprojected',
]
rename = {}
xls = xls_to_dict(r'E:\rks\rucode\new3\composit\composit.xls')
for key in xls:
    if key:
        rename[key] = xls[key]['composit']

def kanids(kanname, index = None):
    ids = []
    parts = kanname.split('KV')
    if index is None:
        for id in parts:
            if len(id) > 10:
                ids.append(('KV'+id).replace('.RRG', ''))
        return ids
    else:
        return [('KV'+parts[index]).replace('.RRG', '')]

def compnewname(compname, rename):
    if compname in rename:
        # print('RENAMED %s TO %s' % (compname, rename[compname]))
        return rename[compname]
    else:
        return compname

def FindEmpty(shpfiles, tifnames, index=None):
    true = []
    false = []
    for shpfile in shpfiles:
        sf, sn, se = split3(shpfile)
        for id in kanids(sn, index):
            if id in tifnames:
                true.append(id)
            else:
                print(id)
                false.append(id)
    return true, false

def CopyComposits(shpfiles, tiffiles, pout, rename=None):
    tifnames = flist(tiffiles, Name)
    for shpfile in shpfiles:
        sf, sn, se = split3(shpfile)
        trueid = sn.replace('.RRG','')
        if rename is not None:
            trueid = compnewname(trueid, rename)
        if trueid in tifnames:
            copyfile(tiffiles[tifnames.index(trueid)], fullpath(pout, trueid, 'tif'))
        else:
            print('NOT FOUND: %s' % trueid)

def ExtractSingles(folder_in, compfiles, pout, index=None):
    files = folder_paths(folder_in,1,'tif')
    names = flist(files, Name)
    cnames = flist(compfiles, Name)
    for cname in cnames:
        for id in kanids(cname, index):
            if id in names:
                copyfile(files[names.index(id)], fullpath(pout,id,'tif'))

def ListCounts(composit_folder, source_folder_list):
    count = {}
    for folder in source_folder_list:
        sources = flist(folder_paths(folder,1,'tif'), Name)
        for name in flist(folder_paths(composit_folder,1,'tif'), Name):
            for id in kanids(name):
                add = int(id in sources)
                if id in count:
                    count[id] = count[id] + add
                else:
                    count[id] = add
    return count

def RenameFiles(folder, rename):
    files = folder_paths(folder,1)
    for file in files:
        f,n,e = split3(file)
        for key in rename:
            if key in n:
                newn = n.replace(key, rename[key])
                newfile = fullpath(f,newn,e)
                if os.path.exists(newfile):
                    print('FILE EXISTS: %s' % newfile)
                else:
                    os.rename(file, fullpath(f,newn,e))
                break

CopyComposits(shpfiles, tiffiles, pout, rename=rename)
RenameFiles(r'e:\rks\rucode\mosaics\source2\source', rename)

sys.exit()
for folder in imgfolderlist:
    ExtractSingles(folder, tiffiles, r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\first_date', 1)
    ExtractSingles(folder, tiffiles, r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\second_date', 2)
FindEmpty(tiffiles, flist(folder_paths(r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\first_date',1,'tif'), Name), 1)
