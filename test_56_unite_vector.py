from geodata import *

pin = r'\\172.21.195.2\FTP-Share\ftp\s3\resursp'
pout = r'\\172.21.195.2\FTP-Share\ftp\s3\resursp\fullcover.shp'

unite_vector(folder_paths(pin,1,'json'), pout)
