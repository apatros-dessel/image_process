# -*- coding: utf-8 -*-

import os, xlwt
from collections import OrderedDict
from PIL import Image
from tools import dict_to_xls

# Filter images from a directory
def filter_image(path):
    export = OrderedDict()
    code_list = []
    file_list = os.listdir(path)
    for file in file_list:
        id, ext = os.path.splitext(file)
        if not ext in ('.tif', '.jpg', '.png'):
            continue
        finish = False
        while True:
            try:
                with Image.open(os.path.join(path, file)) as quicklook:
                    quicklook.show()
                    print(u'Введите числовой индекс сцены {}'.format(file))
                    qualtest = input(' >>> ')
                    if int(qualtest) in (101, 909):
                        raise Exception
                    if qualtest not in code_list:
                        code_list.append(qualtest)
                    export[file] = {'qualtest': str(qualtest)}
                    break
            except:
                try:
                    print(u'Ошибка при оценке снимка, введите 101 чтобы пропустить сцену или 909 чтобы прервать операцию: ')
                    qualtest = input(' >>> ')
                    if qualtest == 101:
                        export[file] = {'qualtest': ''}
                        print(u'Сцена пропущена: {}'.format(id))
                        break
                    if qualtest == 909:
                        finish = True
                        print(u'Операция прервана пользователем')
                        break
                except:
                    pass
        if finish:
            break
    print(u'Список использованных кодов: ')
    print(code_list)
    return export

# Export data to xls
def dict_to_xls2(path2xls, adict): # It's better to use OrderedDict to preserve the order of rows and columns
    wb = xlwt.Workbook()
    ws = wb.add_sheet('New_Sheet')
    # Find all column names
    col_list = ['']
    for row_key in adict:
        for key in adict.get(row_key).keys():
            if not key in col_list:
                col_list.append(key)
    # Write column names
    row = ws.row(0)
    for col_num, col_name in enumerate(col_list):
        row.write(col_num, col_name)
    # Write data
    for id, row_key in enumerate(adict):
        row_num = id+1
        row = ws.row(row_num)
        rowdata = adict.get(row_key)
        if isinstance(rowdata, dict):
            row.write(0, row_key)
            for key in rowdata:
                row.write(col_list.index(key), rowdata.get(key))
        elif hasattr(rowdata, '__iter__'):
            row.write(0, row_num)
            for col_id, obj in enumerate(rowdata):
                row.write(col_id+1, obj)
        else:
            row.write(0, row_num)
            row.write(1, rowdata)
    wb.save(path2xls)
    return None

path = r'd:\terratech\quicklook'
xls_path = path + '\\report.xls'
checkdict = filter_image(path)
dict_to_xls(xls_path, checkdict)
