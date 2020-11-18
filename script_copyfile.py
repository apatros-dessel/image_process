from tools import *
import argparse

parser = argparse.ArgumentParser(description='Given 2 geotiff images finds transformation between')
parser.add_argument('-t', default=None, dest='file_name_template', help='Regular expression for filtering filenames')
parser.add_argument('-f', default=True, dest='copy_folders', help='Preserve file structure or copy all files into the same directory')
parser.add_argument('-d', default=0, dest='renaming_options', help='Actions if endpath is the same')
parser.add_argument('input_folder', help='Folder with source tif files for pansharpening')
parser.add_argument('output_folder', help='Output folder for pansharpened tif files')

args = parser.parse_args()

input_folder = args.input_folder
output_folder = args.output_folder
file_name_template = args.file_name_template
copy_folders = args.copy_folders
renaming_options = int(args.renaming_options)

files = folder_paths(input_folder,1)
path_len = len(input_folder)

if file_name_template:
    file_name_template = str(file_name_template)

if isinstance(copy_folders, str):
    copy_folders = copy_folders.lower()
    if copy_folders=='true':
        copy_folders = True
    elif copy_folders=="false":
        copy_folders = False

for file in files:
    folder, file_name = os.path.split(file)
    if file_name_template:
        if not re.search(file_name_template, file_name):
            continue
    if copy_folders:
        end_path = file[path_len:]
        output_file = os.path.join(output_folder, end_path)
    else:
        output_file = os.path.join(output_folder, file_name)
    if os.path.exists(output_file):
        if renaming_options==0:
            continue
        elif renaming_options==1:
            os.remove(output_file)
        elif renaming_options in (2,3):
            if renaming_options==3:
                if os.path.getsize(file)==os.path.getsize(output_file):
                    continue
            f,n,e = split3(output_file)
            for i in counter(2):
                new_output = '%s\\%s_%i.%s' % (f,n,i,e)
                if not os.path.exists(new_output):
                    output_file = new_output
                    break
    if copy_folders:
        output_foldername = os.path.dirname(output_file)
        suredir(output_foldername)
    shutil.copyfile(file, output_file)