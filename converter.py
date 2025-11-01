from pathlib import Path
from shutil import copy2

from CTkMessagebox import CTkMessagebox
from PIL import Image, UnidentifiedImageError

# Supported image formats
REGISTERED_EXTENSIONS = {ext.lower() for ext in Image.registered_extensions()}
# Max resolution for each format, based on file format specs.
MAX_RESOLUTION = {"webp": (16383, 16383), "png": (65535, 65535)}


class AppLogic:
    def __init__(self):
        self.stop_conversion = False
        self.downscale_all = False
        self.disable_bomb_check_all = False

    def create_folder_tree(self, src_path: Path, dst_path: Path):
        """Copy the source folder tree in the destination path."""

        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)

        for item in src_path.rglob("*"):
            if item.is_dir():
                destination = dst_path / item.relative_to(src_path)
                destination.mkdir(parents=True, exist_ok=True)

    def sort_files(self, src_path, include_subfolders):
        image_files = []
        non_image_files = []

        if include_subfolders:
            files = src_path.rglob("*.*")
        else:
            files = src_path.glob("*.*")

        for file in files:
            extension = file.suffix

            if extension.lower() in REGISTERED_EXTENSIONS:
                image_files.append(file)
            else:
                non_image_files.append(file)

        return image_files, non_image_files

    def convert(self, gui, selected_format):
        """Convert images in the source path to the selected format and save them in the destination path."""
        src_path = Path(gui.fields[0].get().strip())
        dst_path = Path(gui.fields[1].get().strip())
        quality = gui.quality_dropdown.get()
        if not gui.check_params(src_path, dst_path):
            print("Invalid parameters. No changes have been made.")
        gui.convert_button.configure(
            text="Stop",
            fg_color=("light red", "red"),
            hover_color=("dark red"),
            command=lambda: self.request_stop_conversion(),
        )
        dst_path = dst_path / src_path.name
        include_subfolders = gui.include_subfolders.get()
        if include_subfolders:
            self.create_folder_tree(src_path, dst_path)
        else:
            dst_path.mkdir(parents=True, exist_ok=True)

        image_list,non_image_list = self.sort_files(src_path, include_subfolders)

        image_list_length = len(image_list)
        last_print_length = 0
        num_of_converted_files = 0
        num_of_failed_conversions = 0
        num_of_skipped_files = 0
        are_you_sure = False
        for file in image_list:
            if self.stop_conversion:
                break
            image = None
            full_dst_path = dst_path / file.relative_to(src_path)
            print(
                f"Converting {full_dst_path.name} to {selected_format}...",
                end=" " * (last_print_length - len(full_dst_path.name)) + "\r",
            )
            last_print_length = len(f"{full_dst_path.name} to {selected_format}")
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
                    num_of_converted_files += 1
                except Exception as e:
                    print(f"Failed to open {file.name} after disabling decompression bomb check: {e}")
                    num_of_failed_conversions += 1
                    non_image_list.append(file)
                finally:
                    Image.MAX_IMAGE_PIXELS = original_max_image_pixels
            if image:
                max_width, max_height = MAX_RESOLUTION.get(selected_format, (None, None))
                if max_width and max_height and (image.width > max_width or image.height > max_height):
                    if not self.downscale_all:
                        response = CTkMessagebox(
                            title=f"Image too large for {selected_format}",
                            message=f"The image {file.name} has a resolution of {image.width}x{image.height}, which is larger than the maximum supported by the {selected_format} format ({max_width}x{max_height}).\n\nDo you want to downscale or skip it?",
                            icon="question",
                            option_1="Downscale",
                            option_2="Skip",
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
                        elif response == "Yes to all":
                            self.downscale_all = True
                    image.thumbnail((max_width, max_height))
                if not gui.show_overwrite_dialogues(
                    full_dst_path, are_you_sure, selected_format
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
                    full_dst_path.with_suffix("." + selected_format),
                    format=selected_format,
                    lossless=True if quality == "Lossless" else False,
                    quality=int(quality) if quality.isnumeric() else 100,
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
            num_of_converted_files, len(non_image_list)
        ):
            for file in non_image_list:  # TODO: this doesnt work for folders
                copy2(
                    file,
                    dst_path / file.relative_to(src_path),
                )
        # Reset progress bar
        gui.progress.set("0%")
        gui.progressbar_percentage.set("0")
        gui.overwrite_all = False
        self.downscale_all = False
        self.disable_bomb_check_all = False
        gui.show_overwrite_all_dialogue = True

        gui.convert_button.configure(
            state="normal",
            text="Convert",
            fg_color=("light green", "green"),
            hover_color=("light red", "red"),
            command=gui.start_conversion_thread,
        )
        self.stop_conversion = False

    def request_stop_conversion(self):
        self.stop_conversion = True
