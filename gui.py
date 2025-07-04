import multiprocessing as mp
import sys
from pathlib import Path
from tkinter import BooleanVar, DoubleVar, StringVar
from ctypes import c_bool, c_int
from shutil import copy2

import customtkinter as ctk
from converter import Converter
from CTkMessagebox import CTkMessagebox
from PIL import Image

# Supported image formats
REGISTERED_EXTENSIONS = {ext.lower() for ext in Image.registered_extensions()}

def get_resource_path(relative_path):
    """Get the absolute path to a resource in a way that works for development and for PyInstaller/Nuitka bundles."""
    try:
        # PyInstaller/Nuitka creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent

    return Path(base_path) / relative_path


class Gui:
    def __init__(self, root=None):
        if not root:
            self.root = ctk.CTk()
        else:
            self.root = root

        icon_path = get_resource_path("icon.ico")
        self.root.iconbitmap(str(icon_path))

        self.root.title("WebP Crawler")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_size = f"{int(screen_width * 0.32)}x{int(screen_height * 0.21)}"
        min_window_size = "614x226"
        self.root.geometry(
            window_size if window_size >= min_window_size else min_window_size
        )
        self.root.resizable(False, False)
        self.font = ("SegoeUI", 13)

        self.src_path = None 
        self.dst_path = None
        self.quality = None
        self.selected_format = None
        self.include_subfolders = BooleanVar(value=True)
        self.include_subfolders_checkbox = ctk.CTkCheckBox(
            root,
            text="Include subfolders",
            variable=self.include_subfolders,
            onvalue=True,
            offvalue=False,
            font=self.font,
        )

        self.progress = StringVar()
        self.progress.set("0%")
        self.progressbar_percentage = (
            DoubleVar()
        )  # hacky way to include the "%" sign in the progressbar text

        self.overwrite_all = False
        self.show_overwrite_all_dialogue = True

        self.build_window()

    def check_params(self):
        """checks that the source and destination paths are valid and returns them if they are."""
        error_messages = {
            "empty": ("Error", "You must enter both source and destination paths."),
            "same_path": (
                "Error",
                "Source and destination folders cannot be the same.",
            ),
            "not_exist": ("Error", "The source path does not exist."),
            "different_folder": (
                "Select a different folder.",
                "Please select a different destination folder.",
            ),
            "dst_in_src": (
                "Error",
                "Destination folder cannot be inside source folder.",
            ),
        }

        src_basename = self.src_path.name

        if str(self.src_path) == "." or str(self.dst_path) == ".":
            title, message = error_messages["empty"]
        elif not self.src_path.exists():
            title, message = error_messages["not_exist"]
        elif self.src_path == self.dst_path:
            title, message = error_messages["same_path"]

        elif (self.dst_path / src_basename).is_dir():
            use_folder = CTkMessagebox(
                title="Destination folder already exists",
                message=(
                    f"Destination already contains '{src_basename}' inside it."
                    "\nWould you like to use it anyway?",
                ),
                icon="question",
                option_1="Yes",
                option_2="No",
            )
            if use_folder.get() == "Yes":
                return True
            else:
                title, message = error_messages["different_folder"]

        elif str(self.src_path) in str(self.dst_path):
            title, message = error_messages["dst_in_src"]

        else:
            return True

        CTkMessagebox(
            title=title,
            message=message,
            icon="cancel",
            sound=True,
        )
        return False

    def browse(self, path_field, field_num):
        """opens a file selection window and inserts the selected path into the corresponding entry field."""
        # path = ctk.filedialog.askdirectory(
        #     mustexist=True,
        #     title=f"Select {"Source" if field_num == 0 else "Destination"} Folder",
        # )
        # path_field[field_num].delete(0, ctk.END)
        # path_field[field_num].insert(0, path)
        path_field[field_num].insert(0, r"C:\Users\ransh\Downloads\1")
        path_field[field_num+1].insert(0, r"C:\Users\ransh\Downloads\2")

    def build_window(self):
        """builds the window and its widgets."""
        self.header = ctk.CTkLabel(
            self.root, text="─── WebP Crawler ───", font=("Helvetica", 20, "bold")
        )
        self.box1_text = ctk.CTkLabel(
            self.root, text="Source folder:", font=self.font
            )
        self.box2_text = ctk.CTkLabel(
            self.root, text="Destination folder:", font=self.font
        )
        self.convert_button = ctk.CTkButton(
            self.root,
            text="Convert",
            font=self.font,
            fg_color=("light_green", "green"),
            hover_color=("light_red", "red"),
            command=self.start_conversion_process,
        )
        self.box3_text = ctk.CTkLabel(
            self.root, text="Quality:", font=self.font
            )
        self.quality_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=100,
            values=["Lossless", *[str(i) for i in range(95, -1, -1)]],
            font=self.font,
        )
        self.quality_dropdown.set("Lossless")

        self.box4_text = ctk.CTkLabel(
            self.root, text="Format:", font=self.font
            )
        self.format_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=100,
            values=[
                "WebP",
                "PNG",
            ],  # jpeg does not support transparency, so we do not support it.
            font=self.font,
        )
        self.format_dropdown.set("WebP")

        self.progressbar_text = ctk.CTkLabel(
            self.root, textvariable=self.progress, font=self.font
        )

        self.progressbar = ctk.CTkProgressBar(
            self.root,
            variable=self.progressbar_percentage,
            width=300,
            mode="determinate",
        )

        self.header.grid(row=0, column=2, pady=(10, 0))
        self.box1_text.grid(row=3, column=1, sticky="w", padx=(10, 0))
        self.box2_text.grid(row=4, column=1, sticky="w", padx=(10, 0))
        self.box3_text.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        self.quality_dropdown.grid(
            row=5, column=1, sticky="w", padx=(60, 0), pady=(10, 0)
        )

        self.include_subfolders_checkbox.grid(row=5, column=2, pady=(10, 0))

        self.box4_text.grid(row=5, column=3, sticky="w", pady=(15, 0))
        self.format_dropdown.grid(
            row=5, column=3, sticky="w", padx=(45, 0), pady=(10, 0)
        )
        self.convert_button.grid(row=6, column=2)
        self.progressbar_text.grid(row=7, column=2)
        self.progressbar.grid(row=8, column=2)

        self.fields = []
        for i in range(2):
            path_field = ctk.CTkEntry(self.root, width=250)
            path_field.grid(row=i + 3, column=2, pady=(5, 0))
            browse_button = ctk.CTkButton(
                self.root,
                text="Browse...",
                command=lambda field_num=i: self.browse(self.fields, field_num),
            )
            browse_button.grid(row=i + 3, column=3, padx=(5, 0), pady=(5, 0))
            self.fields.append(path_field)

    def start_conversion_process(self):
        """Starts the conversion process in separate processes to prevent the GUI from freezing."""
        conv_settings = self.get_convert_params(gui)
        while not gui.check_params():
            print("Invalid parameters. No changes have been made.")
            conv_settings = gui.get_convert_params(gui)
        self.include_subfolders = gui.include_subfolders.get()
        self.make_subfolders()
        image_list, non_image_list = self.sort_files()
        image_list_length = len(image_list)

        # Create shared objects in a plain dict
        manager = mp.Manager()
        shared_dict = {
            "stop_conversion": mp.Value(c_bool, False),
            "num_of_converted_files": mp.Value(c_int, 0),
            "num_of_failed_conversions": mp.Value(c_int, 0),
            "non_image_list": manager.list(),
            "num_of_skipped_files": mp.Value(c_int, 0),
        }

        self.convert_button.configure(
            text="Stop",
            fg_color=("light red", "red"),
            hover_color=("dark red"),
            command=lambda: self.request_stop_conversion(shared_dict),
        )

        num_of_processes = mp.cpu_count()
        image_files, non_image_files = self.sort_files()
        total_image_list_length = len(image_files)
        images_per_process = self.assign_images_to_processes(image_files, total_image_list_length, num_of_processes)
        self.selected_format = self.format_dropdown.get().lower()

        processes = []
        lock = mp.Lock()
        for image_batch in images_per_process:
            process = mp.Process(
                target=Converter().convert,
                args=(
                    conv_settings[0],  # src_path
                    conv_settings[1],  # dst_path
                    conv_settings[2],  # quality
                    self.selected_format,
                    image_batch,
                    total_image_list_length,
                    shared_dict,
                    lock
                ),
            )
            processes.append(process)
            process.start()

        self.poll_progress(shared_dict, total_image_list_length, lock)

        for process in processes:
            process.join()

        self.post_conversion(shared_dict, self.src_path, self.dst_path, self.selected_format)

    def get_convert_params(self, gui):
        self.src_path = Path(gui.fields[0].get().strip())
        self.dst_path = Path(gui.fields[1].get().strip())
        self.quality = gui.quality_dropdown.get()
        return self.src_path, self.dst_path, self.quality

    def assign_images_to_processes(self, image_list, image_list_length, num_of_proc):
        if image_list_length == 0 or num_of_proc == 0:
            return []
        images_per_thread = max(1, image_list_length // num_of_proc)
        return [
            image_list[i : i + images_per_thread]
            for i in range(0, image_list_length, images_per_thread)
        ]
    
    def sort_files(self):
        image_files = []
        non_image_files = []

        if self.include_subfolders:
            files = self.src_path.rglob("*.*")
        else:
            files = self.src_path.glob("*.*")

        for file in files:
            extension = file.suffix

            if extension.lower() in REGISTERED_EXTENSIONS:
                image_files.append(file)
            else:
                non_image_files.append(file)

        return image_files, non_image_files

    def update_progressbar(
        self,
        num_of_image_files,
        num_of_failed_conversions,
        num_of_skipped_files,
        file_list_length, #TODO: this may be getting a list of only images and not all files
        lock
    ):
        """updates the progress bar and its text."""
        num_of_processed_files = (
            num_of_image_files
            + num_of_failed_conversions
            + num_of_skipped_files
        )
        progress_percentage = num_of_processed_files / file_list_length * 100
        self.progress.set(f"{int(progress_percentage)}%")
        self.progressbar_percentage.set(progress_percentage / 100)

    def poll_progress(self, shared_dict, total_image_list_length, lock, poll_interval=200):
        """Periodically update the progress bar from shared_dict."""
        with lock:
            num_converted = shared_dict["num_of_converted_files"].value
            num_failed = shared_dict["num_of_failed_conversions"].value
            num_skipped = shared_dict["num_of_skipped_files"].value

        self.update_progressbar(
            num_converted,
            num_failed,
            num_skipped,
            total_image_list_length,
            lock
        )

        # If not done, schedule another poll
        if (num_converted + num_failed + num_skipped) < total_image_list_length and not shared_dict["stop_conversion"].value:
            self.root.after(poll_interval, self.poll_progress, shared_dict, total_image_list_length, lock, poll_interval)

    def post_conversion_dialogue(
        self, num_of_converted_files, num_of_failed_conversions
    ):
        """displays the corresponding dialogue after conversion."""
        if num_of_converted_files == 0:
            CTkMessagebox(
                title="Error",
                message="No images were found in source folder.",
                icon="cancel",
                sound=True,
            )
            return False
        elif num_of_failed_conversions > 0:
            copy_non_images = CTkMessagebox(
                title="Copy non-images?",
                message=(
                    f"{num_of_converted_files} files were successfully converted."
                    f"\nFound {num_of_failed_conversions} non-image files."
                    "\nWould you like to copy them to the destination?"
                ),
                icon="question",
                option_1="Yes",
                option_2="No",
            )
            if copy_non_images.get() == "Yes":
                return True
            elif copy_non_images.get() == "No":
                return False

        else:
            CTkMessagebox(
                title="Conversion complete!",
                message=f"{num_of_converted_files} files were successfully converted!",
                icon="check",
                option_1="Ok",
            )
            return False

    # file overwrite dialogues
    def confirm_overwrite_file(self, file_name):
        overwrite = CTkMessagebox(
            title="File already exists",
            message=(
                f'File "{file_name}.{self.selected_format}" already exists in the destination folder.'
                '\nWould you like to overwrite it?',
            ),
            icon="warning",
            option_1="Yes",
            option_2="No",
        )
        if overwrite.get() == "Yes":
            return True
        elif overwrite.get() == "No":
            return False

    def confirm_overwrite_all(self):
        overwrite_all = CTkMessagebox(
            title="Overwrite all?",
            message="Would you like to overwrite all files that already exist in the destination folder?",
            icon="question",
            option_1="Yes",
            option_2="No",
        )
        if overwrite_all.get() == "Yes":
            return True
        elif overwrite_all.get() == "No":
            return False

    def confirm_are_you_sure(self):
        are_you_sure = CTkMessagebox(
            title="Are you sure?",
            message=(
                "Are you sure you want to overwrite all files that already exist in the destination folder?"
                "\nThis action cannot be undone.",
            ),
            icon="warning",
            option_1="Yes",
            option_2="No",
            sound=True,
        )
        if are_you_sure.get() == "Yes":
            return True
        elif are_you_sure.get() == "No":
            return False

    def show_overwrite_dialogues(self, new_dst_path, are_you_sure, lock):
        """checks if file already exists and prompts user to overwrite or skip."""

        new_dst_path = Path(new_dst_path)
        if (new_dst_path.with_suffix("." + self.selected_format)).is_file():
            if self.overwrite_all:
                return True
            else:
                lock.acquire()
                overwrite_file = self.confirm_overwrite_file(
                    new_dst_path.stem, self.selected_format
                )

                if not overwrite_file:
                    return False
                
                lock.release()

                while self.show_overwrite_all_dialogue and not are_you_sure:
                    lock.acquire()
                    self.overwrite_all = self.confirm_overwrite_all()

                    if self.overwrite_all:
                        are_you_sure = self.confirm_are_you_sure()
                        self.overwrite_all = are_you_sure

                    else:
                        self.overwrite_all = False
                        self.show_overwrite_all_dialogue = False
                    
                    lock.release()

        # If the file is to be overwritten, return True.
        return True

    def make_subfolders(self):
        if self.include_subfolders:
            self.create_folder_tree()
        else:
            self.dst_path.mkdir(parents=True, exist_ok=True)

    def create_folder_tree(self):
        """Copy the source folder tree in the destination path."""

        if not self.dst_path.exists():
            self.dst_path.mkdir(parents=True, exist_ok=True)

        for item in self.src_path.rglob("*"):
            if item.is_dir():
                destination = self.dst_path / item.relative_to(self.src_path)
                destination.mkdir(parents=True, exist_ok=True)
    
    def request_stop_conversion(self, shared_dict):
        shared_dict["stop_conversion"].value = True

    def post_conversion(self, shared_dict, src_path, dst_path, selected_format):
        
        if self.post_conversion_dialogue(
            shared_dict["num_of_converted_files"].value, len(shared_dict["non_image_list"])
        ):
            for file in shared_dict["non_image_list"]:
                file_path = Path(file)
                copy2(
                    file_path,
                    dst_path / file_path.relative_to(src_path),
                )
        # Reset progress bar
        self.progress.set("0%")
        self.progressbar_percentage.set("0")
        self.overwrite_all = False

        self.convert_button.configure(
            state="normal",
            text="Convert",
            fg_color=("light green", "green"),
            hover_color=("light red", "red"),
            command=lambda: self.convert(self, selected_format),  # TODO: this is supposed to be starting a thread
        )
        self.stop_conversion = False

if __name__ == "__main__":
    gui = Gui()
    gui.root.mainloop()
