import os
from pathlib import Path
from shutil import copytree, ignore_patterns, copyfile
from PIL import Image, UnidentifiedImageError
from tkinter import filedialog

    

print("Enter path to source folder (a folder that contains either images or folders with images within it):")
src_path = filedialog.askdirectory(mustexist=True).replace("/", "\\")
if src_path == "":
    print("No path entered. Exiting...")
    exit()

print(src_path)
dst_create_folder_name = os.path.basename(os.path.normpath(src_path)) #base folder name to create in dst

print("\nEnter Destination folder for completed conversions:")
dst_path = filedialog.askdirectory(mustexist=True).replace("/", "\\") + "\\" #initial destination
if dst_path == "\\":
    print("No path entered. Exiting...")
    exit()

while src_path in dst_path:                                                                            #this is to prevent converted images from being endlessly re-converted.
    print("\nDestination cannot be contained within the source folder. Please specify a new one:")
    dst_path = filedialog.askdirectory(mustexist=True).replace("/", "\\") + "\\"
print(dst_path)

print("\nConverted image quality: (0-100 or 'lossless')")
quality = input().lower()

while (not quality.isnumeric() or int(quality) < 0 or int(quality) > 100) and quality != "lossless" and quality != "":
    print("Quality must be between 0 and 100:")
    quality = input()


def ignore_files(folder, files):                                                                        #|
    return [f for f in files if not os.path.isdir(os.path.join(folder, f))]                             #|
                                                                                                        #|  copies the directory tree to the destination.
try:                                                                                                    #|
    copytree(src_path, dst_path + dst_create_folder_name,symlinks=False,ignore=ignore_files)            #|
except FileExistsError:
    print("\nDirectory already exists! No files have been converted.")
    exit()


file_list = list(Path(src_path).rglob("*.*"))


num_of_image_files = 0
num_of_non_image_files = 0
last_iter_length = 0
non_image_files = []

for i in file_list:
    new_dst_path = dst_path + os.path.basename(src_path) + str(str(i).split(src_path)[1]) #destination to original tree path
    print(f"Converting {os.path.basename(new_dst_path)}...", end=" " * (last_iter_length - len(os.path.basename(new_dst_path))) + "\r")
    last_iter_length = len(os.path.basename(new_dst_path))

    try:
        image = Image.open(i)
        if quality == "lossless" or quality == "":
            image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", lossless=True)
        
        else:
            image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", quality= int(quality))
        num_of_image_files += 1
    
    except UnidentifiedImageError:
        num_of_non_image_files += 1
        non_image_files.append(i)


if num_of_image_files > 0:
    print(f"\033[A\nSuccessfully converted {num_of_image_files} file(s)!" + " " * last_iter_length)

if num_of_non_image_files >= 1:
    print(f"Could not convert {num_of_non_image_files} file(s). They are most likely not images. Would you like to copy them anyway? (y/n):")
    copy_non_images = input().lower()
    if copy_non_images == "y" or copy_non_images == "yes":
        for i in non_image_files:
            copyfile(i, dst_path + os.path.basename(src_path) + str(str(i).split(src_path)[1]))
        print(f"Copied {num_of_non_image_files} file(s).")
    else:
        pass

input("\nPress any key to exit...")
