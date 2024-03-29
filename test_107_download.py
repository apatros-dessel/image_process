from tools import *
from progress.bar import IncrementalBar

folder_in = r'y:\102_2020_33'
folder_out = r'\\172.21.195.160\thematic\S3_NATAROVA_\102_2020_33'

input_folders, input_files = folder_paths(folder_in)
cut_len = len(folder_in)

def FileMatch(file1, file2):
    return os.path.getsize(file1) == os.path.getsize(file2)

def DownloadAndCheck(ifile, ofile, iter_lim = 10, checksum = True):
    iter = 0
    if checksum:
        icheck = CheckSum(ifile)
        while icheck != CheckSum(ofile):
            if iter > iter_lim:
                print(' ITERATION NUMBER EXEEDED: %s' % Name(ifile))
                return None
            delete(ofile)
            shutil.copyfile(ifile, ofile)
            iter += 1
    else:
        while os.path.getsize(file1) != os.path.getsize(file2):
            if iter > iter_lim:
                print(' ITERATION NUMBER EXEEDED: %s' % Name(ifile))
                return None
            delete(ofile)
            shutil.copyfile(ifile, ofile)
            iter += 1
    return os.path.getsize(ofile)

for ifolder in input_folders:
    if '.PMS' in ifolder:
        continue
    else:
        ofolder = r'%s\%s' % (folder_out, ifolder[cut_len:])
        if os.path.exists(ofolder):
            pass
        else:
            os.makedirs(ofolder)

print('\nSTART %s\n' % os.path.split(folder_in)[1])
copy_size = 0
exists_size = 0
miss_size = 0
error_size = 0
bar = IncrementalBar('Идёт загрузка: ', max = len(input_files))

for ifile in input_files:
    ofile = r'%s\%s' % (folder_out, ifile[cut_len:])
    ofolder, oname = os.path.split(ofile)
    if '.PMS' in ofile:
        miss_size += os.path.getsize(ifile)
    elif os.path.exists(ofile):
        size = DownloadAndCheck(ifile, ofile)
        if size is not None:
            exists_size += size
        else:
            error_size += os.path.getsize(ifile)
    else:
        shutil.copyfile(ifile, ofile)
        size = DownloadAndCheck(ifile, ofile)
        if size is not None:
            copy_size += size
        else:
            error_size += os.path.getsize(ifile)
    bar.next()

print('\nЗагружено: \t%s\nПроверено: \t%s\nПропущено: \t%s\nОшибки: \t%s\n\n Всего: %s\n' %
      (str_size(copy_size), str_size(exists_size), str_size(miss_size), str_size(error_size), str_size(copy_size + exists_size + miss_size + error_size)))
