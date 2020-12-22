from geodata import *
from image_processor import process, scene

proc_path = r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1913'
xls_dict = xls_to_dict(r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1913\cloud_rsp.xls')
path_out = r'\\172.21.195.2\FTP-Share\ftp\image_exchange\rsp_cloud'
imsys = 'RSP'
save_pms = True

proc = process().input(proc_path, imsys_list=[imsys], skip_duplicates=False)

for pathxml in xls_dict:
    if xls_dict[pathxml]['mark']=='1':
        folder, file = os.path.split(pathxml)
        copydir(folder, path_out)
        print('COPY: %s' % folder)
        if save_pms:
            datamask1 = scene(pathxml, imsys).datamask()
            id = xls_dict[pathxml]['id']
            id_pms = id.replace('.MS', '.PMS')
            for ascene in proc.scenes:
                if ascene.meta.id==id_pms:
                    if ShapesIntersect(datamask1, ascene.datamask()):
                        copydir(ascene.path, path_out)
                        print('COPY: %s' % ascene.path)
