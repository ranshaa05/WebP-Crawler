import multiprocessing as mp
from pathlib import Path
from shutil import copy2

from PIL import Image, UnidentifiedImageError


class Converter:
    def __init__(self):
        self.last_print_length = 0
        self.num_of_converted_files = 0
        self.num_of_failed_conversions = 0
        self.num_of_skipped_files = 0
        self.are_you_sure = False

    def convert(self, src_path, dst_path, quality, selected_format, image_list, total_image_list_length, shared_dict, lock):
        """Convert images in the source path to the selected format and save them in the destination path."""
        for file in image_list:
            if shared_dict["stop_conversion"].value:
                break
            image = None
            full_dst_path = dst_path / file.relative_to(src_path)
            print('\033[2K\033[0G', end='')
            print(f"Converting {full_dst_path.name} to {selected_format}...")

            try:
                image = Image.open(file)
            except UnidentifiedImageError:
                with lock:
                    shared_dict["num_of_failed_conversions"].value += 1
                    shared_dict["non_image_list"].append(str(file))
                continue

            # Overwrite logic: always overwrite, or skip if file exists (no GUI prompt)
            output_file = full_dst_path.with_suffix("." + selected_format)
            if output_file.exists():
                # Example: always overwrite. If you want to skip, uncomment the next lines:
                # with lock:
                #     shared_dict["num_of_skipped_files"].value += 1
                # image.close()
                # continue
                pass

            image.save(
                output_file,
                format=selected_format,
                lossless=True if quality == "Lossless" else False,
                quality=int(quality) if quality.isnumeric() else 100,
                subsampling=0,
            )
            image.close()
            with lock:
                shared_dict["num_of_converted_files"].value += 1



    def post_conversion(self, gui, shared_dict, src_path, dst_path, selected_format):
        if gui.post_conversion_dialogue(
            self.num_of_converted_files, len(shared_dict["non_image_list"])
        ):
            for file in shared_dict["non_image_list"]:  # TODO: this doesnt work for folders
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