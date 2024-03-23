import customtkinter as ctk
import os
import threading

from CTkMessagebox import CTkMessagebox
from tkinter import DoubleVar, StringVar

from converter import AppLogic


class Gui:
    def __init__(self, root=None):
        if not root:
            self.root = ctk.CTk()
        else:
            self.root = root

        self.root.title("All To webp")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_size = f"{int(screen_width * 0.32)}x{int(screen_height * 0.2)}"
        min_window_size = "620x220"
        self.root.geometry(window_size if window_size > min_window_size else min_window_size)
        self.font = ("SegoeUI", 13)

        self.header = None
        self.box1_text = None
        self.box2_text = None
        self.box3_text = None
        self.box4_text = None
        self.start_button = None
        self.quality_dropdown = None
        self.format_dropdown = None
        self.fields = None
        self.progressbar = None
        self.progressbar_text = None

        self.progress = StringVar()
        self.progress.set("0%")
        self.progressbar_percentage = DoubleVar()  # hacky way to include the "%" sign in the progressbar text

        self.overwrite_all = False
        self.show_overwrite_all_dialogue = True
        
        self.build_window()

    def check_params(self, src_path, dst_path):
        """checks that the source and destination paths are valid and returns them if they are."""
        error_messages = {
            "empty": ("Error", "You must enter both source and destination paths."),
            "same_path": ("Error", "Source and destination folders cannot be the same."),
            "not_exist": ("Error", "The source path does not exist."),
            "different_folder": ("Select a different folder.", "Please select a different destination folder."),
            "rel_path": ("Error", "Destination folder must be full path."),
            "dst_in_src": ("Error", "Destination folder cannot be inside source folder."),
        }

        src_basename = os.path.basename(src_path)

        if src_path == "" or dst_path == "":
            title, message = error_messages["empty"]
        elif src_path == dst_path:
            title, message = error_messages["same_path"]
        elif not os.path.exists(src_path):
            title, message = error_messages["not_exist"]
        elif not os.path.isabs(dst_path):
            title, message = error_messages["rel_path"]

        elif os.path.isdir(os.path.join(dst_path, src_basename)):
            use_folder = CTkMessagebox(
                title="Destination folder already exists",
                message=f"Destination folder already has a folder named {src_basename} in it.\nWould you like to use it anyway?",
                icon="question",
                option_1="Yes",
                option_2="No",
            )
            if use_folder.get() == "Yes":
                return True
            else:
                title, message = error_messages["different_folder"]

        elif src_path in dst_path:
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
        """opens a file dialog and inserts the selected path into the corresponding entry field."""
        path = ctk.filedialog.askdirectory(
            mustexist=True, title="Select Destination Folder")
        path_field[field_num].delete(0, ctk.END)
        path_field[field_num].insert(0, path)

    def build_window(self):
        """builds the window and its widgets."""
        self.header = ctk.CTkLabel(self.root, text="Enter paths:", font=self.font)
        self.box1_text = ctk.CTkLabel(self.root, text="Source folder:", font=self.font)
        self.box2_text = ctk.CTkLabel(self.root, text="Destination folder:", font=self.font)
        self.start_button = ctk.CTkButton(
            self.root,
            text="Start",
            font=self.font,
            fg_color=("light_green", "green"),
            hover_color=("light_red", "red"),
            command=self.start_conversion_thread
        )
        self.box3_text = ctk.CTkLabel(self.root, text="Quality:", font=self.font)
        self.quality_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=100,
            values=["Lossless", *[str(i) for i in range(95, -1, -1)]],
            font=self.font
        )
        self.quality_dropdown.set("Lossless")
        
        self.box4_text = ctk.CTkLabel(self.root, text="Format:", font=self.font)
        self.format_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=100,
            values=["webp", "png"], #jpeg does not support transparency, so we do not support it.
            font=self.font
        )
        self.format_dropdown.set("webp")

        self.progressbar_text = ctk.CTkLabel(self.root, textvariable=self.progress, font=self.font)

        self.progressbar = ctk.CTkProgressBar(
            self.root,
            variable=self.progressbar_percentage,
            width=300,
            mode="determinate",
        )

        self.header.grid(row=0, column=2, columnspan=1)
        self.box1_text.grid(row=3, column=1, sticky="w", padx=(10, 0))
        self.box2_text.grid(row=4, column=1, sticky="w", padx=(10, 0))
        self.box3_text.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        self.quality_dropdown.grid(row=5, column=1, sticky="w", padx=(60, 0), pady=(5, 0))
        self.box4_text.grid(row=5, column=3, sticky="w", padx=(0, 0), pady=(5, 0))
        self.format_dropdown.grid(row=5, column=3, sticky="w", padx=(45, 0), pady=(5, 0))
        self.start_button.grid(row=6, column=2)
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

    def start_conversion_thread(self):
        self.start_button.configure(state="disabled")
        conversion_thread = threading.Thread(target=lambda: AppLogic().convert(self, self.format_dropdown.get()), daemon=True)
        conversion_thread.start()


    def update_progressbar(
        self,
        num_of_image_files,
        num_of_non_image_files,
        num_of_skipped_files,
        file_list_length,
    ):
        """updates the progress bar and its text."""
        num_of_processed_files = num_of_image_files + num_of_non_image_files + num_of_skipped_files
        progress_percentage = num_of_processed_files / file_list_length * 100
        self.progress.set(f"{int(progress_percentage)}%")
        self.progressbar_percentage.set(progress_percentage / 100)
        

    def post_conversion_dialogue(self, num_of_images, num_of_non_images):
        """displays the corresponding dialogue after the conversion process is complete."""
        if num_of_images == 0:
            CTkMessagebox(
                title="Error",
                message="No images were found in source folder.",
                icon="cancel",
                sound=True,
            )
            return False
        elif num_of_non_images > 0:
            copy_non_images = CTkMessagebox(
                title="Copy non-images?",
                message=f"""{num_of_images} files were successfully converted.
{num_of_non_images} files could not be converted. they are most likely not images.
Copy non-images to destination folder?""",
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
                message=f"{num_of_images} files were successfully converted!",
                icon="check",
                option_1="Ok",
            )
            return False

    # file overwrite dialogues
    def confirm_overwrite_file(self, file_name, selected_format):
        overwrite = CTkMessagebox(
            title="File already exists",
            message=f'File "{file_name}.{selected_format}" already exists in the destination folder.\nWould you like to overwrite it?',
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
            message="Are you sure you want to overwrite all files that already exist in the destination folder?\nThis action cannot be undone.",
            icon="warning",
            option_1="Yes",
            option_2="No",
            sound=True,
        )
        if are_you_sure.get() == "Yes":
            return True
        elif are_you_sure.get() == "No":
            return False

    def show_overwrite_dialogues(self, new_dst_path, are_you_sure, selected_format):
        """check if file already exists and prompt user to overwrite or skip."""
        if os.path.isfile(new_dst_path.split(".")[0] + "." + selected_format):
            if self.overwrite_all:
                return True

            else:
                overwrite_file = self.confirm_overwrite_file(
                    os.path.basename(
                        new_dst_path.split(".")[0]
                    ),
                    selected_format
                )

                if not overwrite_file:
                    return False

                while self.show_overwrite_all_dialogue and not are_you_sure:
                    self.overwrite_all = self.confirm_overwrite_all()

                    if self.overwrite_all:
                        are_you_sure = self.confirm_are_you_sure()
                        self.overwrite_all = are_you_sure

                    else:
                        self.overwrite_all = False
                        self.show_overwrite_all_dialogue = False
        return True  # file is to be overwritten


if __name__ == "__main__":
    gui = Gui()
    gui.root.mainloop()
