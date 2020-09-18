from geodata import *

objects_list = [
    r'\\172.21.195.2\FTP-Share\ftp\!region_shows\krym\Карьеры\Исходное состояние\quarry_Krym.shp',
    r'\\172.21.195.2\FTP-Share\ftp\!region_shows\krym\Эко\ТБО\krym\tbo_krym_narusheniya.shp',
    r'\\172.21.195.2\FTP-Share\ftp\!region_shows\krym\Эко\ТБО\krym\tbo_krym_poligon.shp',
]

cover_path = r'\\172.21.195.2\FTP-Share\ftp\s3\s3cover.shp'
output_path = r'\\172.21.195.2\FTP-Share\ftp\s3\krym_cover_ids.txt'

output_list = []
names_list = []

ds_cover, lyr_cover = get_lyr_by_path(cover_path)
for feat in lyr_cover:
    names_list.append(feat.GetField('id'))

for object_path in objects_list:
    intersection = np.max(intersect_array(cover_path, object_path), axis=0).astype(bool)
    for i, res in enumerate(intersection):
        if res:
            if re.search('KV.*PMS', names_list[i]):
                if not names_list[i] in output_list:
                    output_list.append(names_list[i])

scroll(output_list, lower=len(output_list))

if output_list:
    with open(output_path, 'w') as txt:
        txt.write('*'+'\n*'.join(output_list))
