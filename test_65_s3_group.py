from tools import *

dir = r''
folder_tmpt = r''
dir_out = r''

for folder_name in os.listdir(dir):
    if re.search(folder_tmpt, folder_name):
        command = 'python37 script_quicklook_new_temp.py {} -d {}'.format(
            fullpath(dir,folder_name),
            fullpath(dir_out,folder_name)
        )
        os.system(command)