from pathlib import Path
from tkinter import BooleanVar, DoubleVar, StringVar

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

import converter


class Gui:
    def __init__(self, icon_path,root=None):
        if not root:
            self.root = ctk.CTk()
        else:
            self.root = root
        
        self.root.iconbitmap(str(icon_path))
        self.root.title("WebP Crawler")
        screen_width, screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        min_window_size = "615x225"
        window_size = f"{int(screen_width * 0.32)}x{int(screen_height * 0.21)}"
        self.root.geometry(
            window_size if window_size >= min_window_size else min_window_size
        )
        self.root.resizable(False, False)
        self.font = ("SegoeUI", 14)

        # ui element variables
        self.fields = []
        self.browse_buttons = []
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

        # file overwrite variables
        self.overwrite_all = False
        self.show_overwrite_all_dialogue = True

        self.build_window()


    def build_window(self):
        """builds the window and its widgets."""
        self.__make_widgets__()
        self.__position_widgets__()

    def __make_widgets__(self):
        """define the widgets for the GUI."""
        self.header = ctk.CTkLabel(
            self.root, text="──── WebP Crawler ────", font=("Helvetica", 20, "bold")
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
            font=("SegoeUI", 14, "bold"),
            fg_color=("light_green", "green"),
            hover_color=("light_red", "red"),
            command=lambda: converter.start_conversion_thread(self),
        )
        self.quality_text = ctk.CTkLabel(
            self.root, text="Quality:", font=self.font
            )
        self.quality_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=90,
            values=["Lossless", *[str(i) for i in range(95, -1, -1)]],
            font=self.font,
        )
        self.quality_dropdown.set("Lossless")

        self.format_text = ctk.CTkLabel(
            self.root, text="Format:", font=self.font
            )
        self.format_dropdown = ctk.CTkComboBox(
            self.root,
            state="readonly",
            width=100,
            values=[
                "WebP",
                "PNG",
            ],  # jpeg does not support transparency, so we do not support it🙄.
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

        for i in range(2):
            path_field = ctk.CTkEntry(self.root, width=250)
            browse_button = ctk.CTkButton(
                self.root,
                text="Browse...",
                command=lambda field_num=i: self.__browse__(self.fields, field_num),
            )
            self.fields.append(path_field)
            self.browse_buttons.append(browse_button)
        
    def __position_widgets__(self):
        """positions the UI elements inside the GUI."""
        self.header.grid(row=0, column=2, pady=(10, 0))
        self.box1_text.grid(row=3, column=1, sticky="w", padx=(10, 0))
        self.box2_text.grid(row=4, column=1, sticky="w", padx=(10, 0))
        self.quality_text.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        self.quality_dropdown.grid(
            row=5, column=1, sticky="w", padx=(60, 0), pady=(10, 0)
        )

        self.include_subfolders_checkbox.grid(row=5, column=2, pady=(10, 0))

        self.format_text.grid(row=5, column=3, sticky="w", pady=(15, 0))
        self.format_dropdown.grid(
            row=5, column=3, sticky="w", padx=(50, 0), pady=(10, 0)
        )
        self.convert_button.grid(row=6, column=2)
        self.progressbar_text.grid(row=7, column=2)
        self.progressbar.grid(row=8, column=2)

        for i in range(2):
            self.fields[i].grid(row=i + 3, column=2, pady=(5, 0))
            self.browse_buttons[i].grid(row=i + 3, column=3, padx=(5, 0), pady=(5, 0))


    def __browse__(self, path_field, field_num):
        """opens a file selection window and inserts the selected path into the corresponding entry field."""
        path = ctk.filedialog.askdirectory(
            mustexist=True,
            title=f"Select {"Source" if field_num == 0 else "Destination"} Folder",
        )
        path_field[field_num].delete(0, ctk.END)
        path_field[field_num].insert(0, path)

    def update_progressbar(
        self,
        num_of_image_files,
        num_of_failed_conversions,
        num_of_skipped_files,
        file_list_length,
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

    def post_conversion_dialogue(
        self, num_of_converted_files, num_of_failed_conversions, num_of_already_formatted_images
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
                message=f"{num_of_converted_files} files were successfully converted."
                "\nFound {num_of_failed_conversions} non-image files."
                "\nWould you like to copy them to the destination?",
                icon="question",
                option_1="Yes",
                option_2="No",
            )
            if copy_non_images.get() == "Yes":
                return True
            else:
                return False

        else:
            message = f"{num_of_converted_files} files were successfully converted!"
            if num_of_already_formatted_images > 0:
                message += f"\nCopied {num_of_already_formatted_images} {self.format_dropdown.get().upper()} files!"
            CTkMessagebox(
                title="Conversion complete!",
                message=message,
                icon="check",
                option_1="Ok",
            )
            return False
        
    def reencode_images_of_same_format_dialogue(self, selected_format, num_of_already_formatted_images):
        if num_of_already_formatted_images == 0:
            return False
        reencode_images = CTkMessagebox(
            title="Re-encode images?",
            message=f"Found {num_of_already_formatted_images} images that are already {selected_format.upper()}.\nWould you like to re-process them, or copy as-is?",
            icon="question",
            option_1="Copy",
            option_2="Re-encode",
        )
        if reencode_images.get() == "Re-encode":
            return True
        elif reencode_images.get() == "Copy":
            return False

    # file overwrite dialogues
    def show_overwrite_dialogues(self, new_dst_path, are_you_sure, selected_format):
        """checks if file already exists and prompts user to overwrite or skip."""
        new_dst_path = Path(new_dst_path)
        if (new_dst_path.with_suffix("." + selected_format)).is_file():
            if self.overwrite_all:
                return True
            else:
                overwrite_file = self.__open_overwrite_dialogue_box__(
                    title="File already exists",
                    message=f'File "{new_dst_path.stem}.{selected_format}" already exists in the destination folder.'
                    '\nWould you like to overwrite it?',
                    icon="warning",
                )

                if not overwrite_file:
                    return False

                while self.show_overwrite_all_dialogue and not are_you_sure:
                    self.overwrite_all = self.__open_overwrite_dialogue_box__(
                        title="Overwrite all?",
                        message="Would you like to overwrite all files that already exist in the destination folder?",
                        icon="question",
                    )

                    if self.overwrite_all:
                        are_you_sure = self.__open_overwrite_dialogue_box__(
                            title="Are you sure?",
                            message="Are you sure you want to overwrite all files that already exist in the destination folder?"
                            "\nThis action cannot be undone.",
                            icon="warning",
                        )
                        self.overwrite_all = are_you_sure

                    else:
                        self.overwrite_all = False
                        self.show_overwrite_all_dialogue = False
        return True  # file is to be overwritten
    
    def __open_overwrite_dialogue_box__(self, title, message, icon):
        overwrite = CTkMessagebox(
            title=title,
            message=message,
            icon=icon,
            option_1="Yes",
            option_2="No",
        )
        if overwrite.get() == "Yes":
            return True
        else:
            return False