import os
import logging
import coloredlogs

from pathlib import Path
from shutil import copytree, ignore_patterns, copyfile
from PIL import Image, UnidentifiedImageError

# logger setup
log = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=log)


class AppLogic:
    def __init__(self):
        self.last_iter_length = 0
        self.non_image_files = []

    def create_folder_tree(self, src_path, dst_path):
        # copies the directory tree to the destination.
        def ignore_files(folder, files):
            return [f for f in files if not os.path.isdir(os.path.join(folder, f))]

        try:
            copytree(
                src_path,
                os.path.join(dst_path, os.path.basename(os.path.normpath(src_path))),
                symlinks=False,
                ignore=ignore_files,
            )
        except FileExistsError:
            return False

    def convert(self):
        src_path = self.fields[0].get().strip()
        dst_path = self.fields[1].get().strip()
        quality = self.quality_dropdown.get()
        if self.check_params(src_path, dst_path):
            AppLogic().create_folder_tree(src_path, dst_path)
            pass

            file_list = list(Path(src_path).rglob("*.*"))
            file_list_length = len(file_list)
            last_iter_length = 0  # TODO: make these class variables
            num_of_image_files = 0
            num_of_non_image_files = 0
            num_of_skipped_files = 0
            non_image_files = []
            are_you_sure = False
            for file in file_list:
                image = None
                new_dst_path = f"{dst_path}\\{os.path.basename(src_path) + str(file).split(src_path)[1]}"  # destination to original tree path

                print(
                    f"Converting {os.path.basename(new_dst_path)}...",
                    end=" " * (last_iter_length - len(os.path.basename(new_dst_path)))
                    + "\r",
                )
                last_iter_length = len(os.path.basename(new_dst_path))

                try:
                    image = Image.open(file)
                    num_of_image_files += 1
                except UnidentifiedImageError:
                    num_of_non_image_files += 1
                    non_image_files.append(file)

                if image:
                    if not self.show_overwrite_dialogues(new_dst_path, are_you_sure):
                        num_of_skipped_files += 1
                        image.close()
                        self.update_progressbar(
                            num_of_image_files,
                            num_of_non_image_files,
                            num_of_skipped_files,
                            file_list_length,
                        )
                        continue  # continue if user chooses to skip overwriting this file.

                    if quality == "Lossless":
                        image.save(
                            new_dst_path[: new_dst_path.rfind(".")] + ".webp",
                            format="webp",
                            lossless=True,
                        )
                    else:
                        image.save(
                            new_dst_path[: new_dst_path.rfind(".")] + ".webp",
                            format="webp",
                            quality=int(quality),
                        )
                    image.close()
                    image = None

                self.update_progressbar(
                    num_of_image_files,
                    num_of_non_image_files,
                    num_of_skipped_files,
                    file_list_length,
                )

            if self.post_conversion_dialogue(
                num_of_image_files, num_of_non_image_files
            ):
                for file in non_image_files:
                    copyfile(
                        file,
                        os.path.join(
                            dst_path,
                            os.path.basename(src_path),
                            str(file).split(src_path + "\\")[1],
                        ),
                    )

            # Reset progress bar
            self.progress.set("0%")
            self.display_progress.set("0")

            self.overwrite_all = False  # reset overwrite all flag

        else:
            log.warn("Invalid parameters. No changes have been made.")
