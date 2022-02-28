import os
from pathlib import Path
from shutil import copytree, ignore_patterns, copyfile
from PIL import Image, UnidentifiedImageError


class AppLogic:
    def __init__(self):
       self.file_list = None
       self.num_of_image_files = 0
       self.num_of_non_image_files = 0
       self.last_iter_length = 0
       self.non_image_files = []

    

    def create_folder_tree(self, src_path, dst_path):
        def ignore_files(folder, files):                                                                                        #|
            return [f for f in files if not os.path.isdir(os.path.join(folder, f))]                                             #|
                                                                                                                                #|  copies the directory tree to the destination.
        try:                                                                                                                    #|
            copytree(src_path, dst_path + os.path.basename(os.path.normpath(src_path)),symlinks=False,ignore=ignore_files)      #|
        except FileExistsError:
            return False



    def convert(self, src_path, dst_path, quality):
        self.file_list = Path(src_path).rglob('*.*')
        for i in self.file_list:
            new_dst_path = dst_path + os.path.basename(src_path) + str(i).split(src_path)[1]  #destination to original tree path
            print(f"Converting {os.path.basename(new_dst_path)}...", end=" " * (self.last_iter_length - len(os.path.basename(new_dst_path))) + "\r")
            last_iter_length = len(os.path.basename(new_dst_path))

            try:
                image = Image.open(i)
                if quality.lower() == "lossless":
                    image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", lossless=True)
                else:
                    image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", quality= int(quality))

                self.num_of_image_files += 1
            except UnidentifiedImageError:
                self.num_of_non_image_files += 1
                self.non_image_files.append(i)

            



        if self.num_of_image_files > 0:
            print(f"\033[A\nSuccessfully converted {self.num_of_image_files} file(s)!" + " " * last_iter_length)

        if self.num_of_non_image_files >= 1:
            print(f"Could not convert {self.num_of_non_image_files} file(s). They are most likely not images. Would you like to copy them anyway? (y/n):")
            copy_non_images = input().lower()
            if copy_non_images == "y" or copy_non_images == "yes":
                for i in self.non_image_files:
                    copyfile(i, dst_path + os.path.basename(src_path) + str(str(i).split(src_path)[1]))
                print(f"Copied {self.num_of_non_image_files} file(s).")
            elif copy_non_images == "n" or copy_non_images == "no":
                pass
            else:
                print("Invalid input. No files have been copied.") #TODO: will not be needed in GUI version
