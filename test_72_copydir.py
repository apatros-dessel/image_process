from tools import *

xls_dict = xls_to_dict(r'\\172.21.195.215\thematic\source\ntzomz\102_2020_1913\report.xls')

for pathxml in xls_dict:
    if xls_dict[pathxml]['mark']=='1':
        folder, file = os.path.split(pathxml)
        copydir(folder, r'\\172.21.195.2\FTP-Share\ftp\image_exchange\kanopus_cloud')
