from tools import *
from progress.bar import IncrementalBar

folder_in = r'y:\102_2020_107'
folder_out = r'\\172.21.195.160\thematic\S3_NATAROVA_\102_2020_107'

input_folders, input_files = folder_paths(folder_in)
cut_len = len(folder_in)

def FileMatch(file1, file2):
    file1_meta = os.stat(file1)
    file2_meta = os.stat(file2)
    # print(file1_meta)
    # print(file2_meta)
    return file1_meta.st_size == file2_meta.st_size

def CheckSumMatch(file1, file2):
    return CheckSum(file1) == CheckSum(file2)

def DownloadAndCheck(ifile, ofile):
    check = CheckSum(ifile)
    while check != CheckSum(ofile):
    # while FileMatch(file1, file2):
        print('MISMATCHING IN %s, DOWNLOADING AGAIN' % oname)
        delete(ofile)
        shutil.copyfile(ifile, ofile)
    return os.path.getsize(ofile)

miss_size = 0

for ifolder in input_folders:
    if '.PMS' in ifolder:
        miss_size += count_dirsize(ifolder)
        print('MISSED: "%s"' % ifolder[cut_len:])
        continue
    else:
        ofolder = r'%s\%s' % (folder_out, ifolder[cut_len:])
        if os.path.exists(ofolder):
            # print('EXISTS: "%s"' % ifolder[cut_len:])
            pass
        else:
            os.makedirs(ofolder)
            print('CREATED: "%s"' % ifolder[cut_len:])

copy_size = 0
exists_size = 0
bar = IncrementalBar('Downloading', max = len(input_files))

for ifile in input_files:
    ofile = r'%s\%s' % (folder_out, ifile[cut_len:])
    ofolder, oname = os.path.split(ofile)
    if os.path.exists(ofolder):
        while not os.path.exists(ofile):
            shutil.copyfile(ifile, ofile)
        if os.path.exists(ofile):
            exists_size += DownloadAndCheck(ifile, ofile)
            # print('EXISTS: "%s"' % oname)
            pass
        else:
            shutil.copyfile(ifile, ofile)
            copy_size += DownloadAndCheck(ifile, ofile)
            # print('COPYIED: "%s"' % oname)
        # print('{}: {}'.format(oname, FileMatch(ifile, ofile)))
    bar.next()

print(str_size(copy_size), str_size(exists_size), str_size(miss_size))
