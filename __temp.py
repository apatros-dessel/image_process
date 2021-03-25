from geodata import *

path = r'\\172.21.195.2\thematic\!projects\Rucode\images_fin\composits\8_ch'
out = r'e:\rks\source\kanopus_test\Rucode\composite\test\8_bands'
names = folder_paths(path,1,'tif')
source = r'e:\rks\source\kanopus_test\Rucode\source'
outxls = r'e:\rks\source\kanopus_test\Rucode\reproject\komposit_list.xls'

def GetRasterDataParams(path):
    raster = gdal.Open(path)
    if raster:
        params = [raster.RasterXSize, raster.RasterYSize]
        for num in range(1, raster.RasterCount+1):
            band = raster.GetRasterBand(num)
            params.append(flist(band.GetStatistics(1,1), round))
        return params

def RasterMatchCheck(files):
    matches = []
    data_params = flist(files, GetRasterDataParams)
    scroll(data_params)
    for i, param1 in enumerate(data_params):
        if param1 is not None:
            for j, param2 in enumerate(data_params):
                if param2 is not None:
                    if i!=j:
                        if param1==param2:
                            matches.append((files[i],files[j]))
    return matches

scroll(RasterMatchCheck(folder_paths(r'\\172.21.195.2\exchanger\fetsival',1,'tif')))


sys.exit()
xls = xls_to_dict(r'\\172.21.195.2\thematic\!SPRAVKA\S3\report_KV_fall.xls')
out = r'e:\rks\source\kv_fall'
res = []
for jpg in xls:
    if int(xls[jpg]['mark'])==1:
        f,n,e = split3(jpg)
        res.append(n)
with open(r'C:\Users\admin\Desktop\list5.txt', 'w') as txt:
    txt.write('\n'.join(res))


for file in names:
    name = split3(file)[1]
    basics = name.split('.L2')
    old = basics[0] + '.L2'
    new = basics[1] + '.L2'
    if 'RRG' in basics[2]:
        continue
    channels = [1,2,3,4,1,2,3,4]
    line = OrderedDict()
    for file in source_files:
        if old in file:
            line['old'] = old
        elif new in file:
            line['new'] = new
    if line.get('old') and line.get('new'):
        line['composit'] = name
        line['channels'] = '1,2,3,4,1,2,3,4'
        report[name] = line
    else:
        print('Wrong name: %s' % name)

dict_to_xls(outxls,report)
