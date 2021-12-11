from webptools import cwebp
import os
from pathlib import Path
from shutil import copytree, ignore_patterns
from elevate import elevate

elevate() #needed for os.isdir()
    


print("Enter path to root folder (a folder that contains either images or folders with images within it):")
img_path = input()
while not os.path.isdir(img_path):
    print("Path does not exist. Please specify a new one:")
    img_path = input()
dst_create_folder_name = os.path.basename(os.path.normpath(img_path)) #base folder name to create in dst

    
print("Enter Destination folder for completed conversions:")
dst_path = input() + "\\" #initial destination
if not os.path.isdir(dst_path[:-1]):
    print("Path does not exist. Please specify a new one:")
    dst_path = input() + "\\"

print("Converted image quality: (0-100)")
quality = input()
if quality == "":
    quality = "100"

while not quality.isnumeric() or int(quality) < 0 or int(quality) > 100:
    print("Quality must be between 0 and 100:")
    quality = str(int(input()))


def ignore_files(folder, files):                                                                        #|
    return [f for f in files if not os.path.isdir(os.path.join(folder, f))]                             #|
                                                                                                        #|  copies the directory tree to the destination.
try:                                                                                                    #|
    copytree(img_path, dst_path + dst_create_folder_name,symlinks=False,ignore=ignore_files)            #|
except FileExistsError:
    print("\nDirectory already exists! No files have been converted.")
    exit()


files = list(Path(img_path).rglob("*.*"))
file_list = []

for i in files:
    file_list.append(i)         #get full file paths


num_of_image_files = 0
num_of_non_image_files = 0
last_iter_length = 0

for i in file_list:
    new_dst_path = dst_path + os.path.basename(img_path) + str(str(i).split(img_path)[1]) #destination to original tree path
    print("Converting " + os.path.basename(new_dst_path) + "...", end=" " * (last_iter_length - len(os.path.basename(new_dst_path))) + "\r")
    last_iter_length = len(os.path.basename(new_dst_path))

    cwebp_output = cwebp(input_image='"' + str(i) + '"', output_image=('"' + new_dst_path + '"')[:new_dst_path.rfind(".")] + ".webp", option="-q " + quality, logging="")  #create webp files. # the quotes are a workaround for a bug in cwebp
    

    if cwebp_output["exit_code"] != 0:
        num_of_non_image_files += 1
    else:
        num_of_image_files += 1
    
    


if num_of_image_files > 0:
    print("Successfully converted " + str(num_of_image_files) + " files!")

if num_of_non_image_files >= 1:
    print("Could not convert " + str(num_of_non_image_files) + " files. Are they not images?")

input("\nPress any key to exit...")
