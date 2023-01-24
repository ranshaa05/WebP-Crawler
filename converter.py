import os
from pathlib import Path
from shutil import copytree, ignore_patterns, copyfile
from PIL import Image, UnidentifiedImageError

import gui

class AppLogic():
    def __init__(self):
        self.last_iter_length = 0
        self.non_image_files = []

    def create_folder_tree(self, src_path, dst_path):
        def ignore_files(folder, files):                                                                                        #|
            return [f for f in files if not os.path.isdir(os.path.join(folder, f))]                                             #|
                                                                                                                                #|  copies the directory tree to the destination.
        try:                                                                                                                  #|
            copytree(src_path, dst_path + "\\" + os.path.basename(os.path.normpath(src_path)),symlinks=False,ignore=ignore_files)      #|
        except FileExistsError:
            return False

    def convert(self):
        src_path = self.fields[0].get().rstrip(" ")
        dst_path = self.fields[1].get().rstrip(" ")
        quality = self.quality_dropdown.get()
        if self.check_params(src_path, dst_path):
            AppLogic().create_folder_tree(src_path, dst_path)
            pass
        else:
            raise ValueError("Invalid parameters.")
        
        file_list = list(Path(src_path).rglob('*.*'))
        last_iter_length = 0          #TODO: make these class variables
        num_of_image_files = 0
        num_of_non_image_files = 0
        total_num_of_files = 0
        non_image_files = []
        for i in file_list:
            new_dst_path = dst_path + "\\" + os.path.basename(src_path) + str(i).split(src_path)[1]  #destination to original tree path
            print(f"Converting {os.path.basename(new_dst_path)}...", end=" " * (last_iter_length - len(os.path.basename(new_dst_path))) + "\r")
            last_iter_length = len(os.path.basename(new_dst_path))

            try:
                image = Image.open(i)
                if quality == "Lossless":
                    image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", lossless=True)
                else:
                    image.save(new_dst_path[:new_dst_path.rfind(".")] + ".webp", format="webp", quality= int(quality))

                num_of_image_files += 1
            except UnidentifiedImageError:
                num_of_non_image_files += 1
                non_image_files.append(i)
            
            total_num_of_files += 1
            self.progress.set(int((total_num_of_files / len(list(file_list))) * 100))
            self.update_progressbar()
        

        if self.post_conversion_dialogue(num_of_image_files, num_of_non_image_files):
            for i in non_image_files:
                copyfile(i, dst_path + "\\" + os.path.basename(src_path) + str(str(i).split(src_path)[1]))
        self.progress.set(0)
        
