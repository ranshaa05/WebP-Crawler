from pathlib import Path
from shutil import copy2

from PIL import Image, UnidentifiedImageError

# Supported image formats
REGISTERED_EXTENSIONS = {ext.lower() for ext in Image.registered_extensions()}


class AppLogic:
    def __init__(self):
        self.stop_conversion = False

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
            if image:
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

        gui.convert_button.configure(
            state="normal",
            text="Convert",
            fg_color=("light green", "green"),
            hover_color=("light red", "red"),
            command=lambda: self.convert(gui, selected_format),  # TODO: this is supposed to be starting a thread
        )
        self.stop_conversion = False

    def request_stop_conversion(self):
        self.stop_conversion = True
