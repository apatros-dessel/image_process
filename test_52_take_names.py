from geodata import *

objects_list = [
    r'\\172.21.195.2\FTP-Share\ftp\цифровая земля\Эко-мониторинг\krasnoyarskaya\TBO_krasnoyarsk_point.shp',
]

cover_path = [
    r'\\172.21.195.2/FTP-Share/ftp/s3/krasnoyarsk_ms/fullcover.shp',
    # r'e:\rks\s3\kanopus_pms\fullcover.shp'
    ]

id_tmpt = 'KV.*P?MS'

output_path = r'e:\rks\s3\kanopus_pms\names_TBO_krasnoyarsk_ms.txt'

output_list = []
names_list = []

for cover in cover_path:
    ds_cover, lyr_cover = get_lyr_by_path(cover)
    for feat in lyr_cover:
        names_list.append(feat.GetField('id'))
    for object_path in objects_list:
        intersection = np.max(intersect_array(cover, object_path), axis=0).astype(bool)
        for i, res in enumerate(intersection):
            if res:
                if re.search(id_tmpt, names_list[i]):
                    if not names_list[i] in output_list:
                        output_list.append(names_list[i].replace('.MS.','.PMS.'))

scroll(output_list, lower=len(output_list))

if output_list:
    with open(output_path, 'w') as txt:
        txt.write('\n'.join(output_list))
