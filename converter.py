import threading
from pathlib import Path
from shutil import copy2

from CTkMessagebox import CTkMessagebox
from PIL import Image, UnidentifiedImageError

import filesystem_utils
import path_validator

# Max resolution for each format, based on file format specs.
MAX_RESOLUTION = {"webp": (16383, 16383), "png": (65535, 65535)}

def start_conversion_thread(gui):
    """starts the conversion process in a separate thread to prevent the GUI from freezing."""
    conversion_thread = threading.Thread(
        target=lambda: Converter().convert(gui),
        daemon=True,
    )
    conversion_thread.start()


class Converter:
    def __init__(self):
        self.stop_conversion = False
        self.downscale_all = False
        self.disable_bomb_check_all = False
        self.src_path = None
        self.dst_path = None
        self.quality = None
        self.include_subfolders = None
        self.selected_format = None

    def __update_ui_params__(self, gui):
        self.src_path = Path(gui.fields[0].get().strip())
        self.dst_path = Path(gui.fields[1].get().strip())
        self.quality = gui.quality_dropdown.get()
        self.include_subfolders = gui.include_subfolders.get()
        self.selected_format = gui.format_dropdown.get().lower()
    
    def __pre_conversion_setup__(self, gui):
        gui.convert_button.configure(
            text="Stop",
            fg_color=("light red", "red"),
            hover_color=("dark red"),
            command=lambda: self.__request_stop_conversion__(),
        )

        filesystem_utils.make_destination_folders(self.src_path, self.dst_path, self.include_subfolders)

        image_list, non_image_list, already_formatted_images = filesystem_utils.detect_images(self.src_path, self.include_subfolders, self.selected_format)
        return (
            image_list,
            non_image_list,
            already_formatted_images
        )
    

    def convert(self, gui):
        """Convert images in the source path to the selected format and save them in the destination path."""
        self.__update_ui_params__(gui)
        if not path_validator.check_paths(self.src_path, self.dst_path):
            self.__reset_convert_button__(gui)
            return # TODO: all of this pre-conversion stuff shouldnt be running in multithreading
        (
            image_list,
            non_image_list,
            already_formatted_images
        ) = self.__pre_conversion_setup__(gui)
        

        self.dst_path = self.dst_path / self.src_path.name
        reencode_images = gui.reencode_images_of_same_format_dialogue(self.selected_format, len(already_formatted_images)) if already_formatted_images else False
        image_list = image_list if reencode_images else [img for img in image_list if img not in already_formatted_images]
        image_list_length = len(image_list)

        num_of_converted_files = 0
        num_of_failed_conversions = 0
        num_of_skipped_files = 0
        are_you_sure = False
        for file in image_list:
            if self.stop_conversion:
                break
            image = None
            full_dst_path = self.dst_path / file.relative_to(self.src_path)
            print(f"\x1b[2KConverting {full_dst_path.name} to {self.selected_format}...", end="\r")
            try:
                image = Image.open(file)
                num_of_converted_files += 1
            except UnidentifiedImageError:
                num_of_failed_conversions += 1
                non_image_list.append(file)
            except Image.DecompressionBombError:
                if not self.disable_bomb_check_all:
                    response = CTkMessagebox(
                        title="Image too large",
                        message=f"The image {file.name} is very large and could be a decompression bomb, which could harm your computer.\n\nWould you like to open it anyway?",
                        icon="warning",
                        option_1="Yes",
                        option_2="No",
                        option_3="Yes to all",
                    )
                    if response.get() == "No" or response is None:
                        num_of_skipped_files += 1
                        gui.update_progressbar(
                            num_of_converted_files,
                            num_of_failed_conversions,
                            num_of_skipped_files,
                            image_list_length,
                        )
                        continue
                    elif response.get() == "Yes to all":
                        self.disable_bomb_check_all = True
                
                original_max_image_pixels = Image.MAX_IMAGE_PIXELS
                Image.MAX_IMAGE_PIXELS = None
                try:
                    image = Image.open(file)
                except Exception as e:
                    print(f"Failed to open {file.name} after disabling decompression bomb check: {e}")
                    num_of_failed_conversions += 1
                    non_image_list.append(file)
                finally:
                    Image.MAX_IMAGE_PIXELS = original_max_image_pixels

            if image:
                max_width, max_height = MAX_RESOLUTION.get(self.selected_format, (None, None))
                if max_width and max_height and (image.width > max_width or image.height > max_height):
                    if not self.downscale_all:
                        response = CTkMessagebox(
                            title=f"Image too large for {self.selected_format}",
                            message=f"The image {file.name} has a resolution of {image.width}x{image.height}, which is larger than the maximum supported by the {self.selected_format} format ({max_width}x{max_height}).\n\nSkip or downscale it?",
                            icon="question",
                            option_1="Skip",
                            option_2="Downscale",
                            option_3="Downscale all",
                        )
                        if response.get() == "Skip" or response is None:
                            num_of_skipped_files += 1
                            image.close()
                            gui.update_progressbar(
                                num_of_converted_files,
                                num_of_failed_conversions,
                                num_of_skipped_files,
                                image_list_length,
                            )
                            continue
                        elif response.get() == "Downscale":
                            pass
                        elif response.get() == "Downscale all":
                            self.downscale_all = True
                            num_of_converted_files += 1

                    original_max = Image.MAX_IMAGE_PIXELS # remove decomp bomb check for downscaling only
                    Image.MAX_IMAGE_PIXELS = None
                    image.thumbnail((max_width, max_height)) # resizes the image
                    Image.MAX_IMAGE_PIXELS = original_max
                    
                if not gui.show_overwrite_dialogues(
                    full_dst_path, are_you_sure, self.selected_format
                ):
                    num_of_skipped_files += 1
                    image.close()
                    gui.update_progressbar(  # TODO:this fails on repeated conversions. might be because it's not running in the gui (main) thread.
                        num_of_converted_files,
                        num_of_failed_conversions,
                        num_of_skipped_files,
                        image_list_length,
                    )
                    continue  # continue if user skips overwriting this file.

                image.save(
                    full_dst_path.with_suffix("." + self.selected_format),
                    format=self.selected_format,
                    lossless=True if self.quality == "Lossless" else False,
                    quality=int(self.quality) if self.quality.isnumeric() else 100,
                    subsampling=0,
                )
                image.close()
                image = None

            gui.update_progressbar(
                num_of_converted_files,
                num_of_failed_conversions,
                num_of_skipped_files,
                image_list_length,
            )
        if gui.post_conversion_dialogue(
            num_of_converted_files, len(non_image_list), len(already_formatted_images) if not reencode_images else 0
        ):
            for file in non_image_list:  # TODO: this doesnt work for folders
                copy2(
                    file,
                    self.dst_path / file.relative_to(self.src_path),
                )

        if not reencode_images:
            for file in already_formatted_images:
                copy2(
                    file,
                    self.dst_path / file.relative_to(self.src_path),
                )
        # Reset progress bar
        gui.progress.set("0%")
        gui.progressbar_percentage.set("0")
        gui.overwrite_all = False
        self.skip_all = False
        self.disable_bomb_check_all = False
        gui.show_overwrite_all_dialogue = True

        self.__reset_convert_button__(gui)

    def __request_stop_conversion__(self):
        self.stop_conversion = True

    def __reset_convert_button__(self, gui): #TODO: move to gui.py
        gui.convert_button.configure(
            state="normal",
            text="Convert",
            fg_color=("light green", "green"),
            hover_color=("light red", "red"),
            command=lambda: start_conversion_thread(gui),
        )
        self.stop_conversion = False
