import tkinter as tk
from tkinter import ttk
from tkinter import filedialog  # tkinter bug
from tkinter import IntVar, StringVar
from os import path


import converter


class Gui:
    def __init__(self, root=None):
        if not root:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title("All To webp")
        self.root.geometry("480x200")

        self.header = None
        self.box1_text = None
        self.box2_text = None
        self.box3_text = None
        self.box4_text = None
        self.start_button = None
        self.quality_dropdown = None
        self.fields = None
        self.progressbar = None
        self.progressbar_text = None

        self.progress = StringVar()
        self.progress.set("0%")
        self.display_progress = (
            IntVar()
        )  # hacky way to include the "%" sign in the progressbar text

    def check_params(self, src_path, dst_path):
        if src_path == "" or dst_path == "\\":  # check if paths are usable
            tk.messagebox.showerror(
                "Error", "You must enter a source and destination path."
            )
        elif src_path == dst_path:
            tk.messagebox.showerror(
                "Error", "Source and destination folders cannot be the same."
            )
        elif not path.exists(src_path):
            tk.messagebox.showerror(
                "Error",
                "Source folder does not exist.\nPlease select a different folder.",
            )
        elif not path.exists(dst_path):
            tk.messagebox.showerror(
                "Error",
                "Destination folder does not exist.\nPlease select a different folder.",
            )
        elif path.isdir(
            dst_path + path.basename(src_path)
        ):  # TODO: maybe add an option to override current folder?
            tk.messagebox.showerror(
                "Error",
                f'Destination folder already has a folder named "{path.basename(src_path)}" in it.\nPlease select a different destination folder.',
            )

        else:
            return src_path, dst_path

    def browse(self, path_field, field_num):
        path = tk.filedialog.askdirectory(
            mustexist=True, title="Select Destination Folder"
        ).replace("/", "\\")
        path_field[field_num].delete(0, tk.END)
        path_field[field_num].insert(0, path)

    def build_window(self):
        self.header = tk.Label(self.root, text="Enter path:")
        self.box1_text = tk.Label(self.root, text="Source folder:")
        self.box2_text = tk.Label(self.root, text="Destination folder:")
        self.start_button = tk.Button(
            self.root, text="Start", command=lambda: converter.AppLogic.convert(self)
        )
        self.box3_text = tk.Label(self.root, text="Quality:")
        self.quality_dropdown = ttk.Combobox(self.root, state="readonly", width=15)
        self.quality_dropdown["values"] = (
            "Lossless",
            *[str(i) for i in range(100, -1, -1)],
        )
        self.quality_dropdown.current(0)
        # TODO: find a way to add a "%" to the end of progressbar_text"
        self.progressbar_text = tk.Label(self.root, textvariable=self.progress)

        self.progressbar = ttk.Progressbar(
            self.root,
            variable=self.display_progress,
            orient="horizontal",
            length=300,
            mode="determinate",
        )

        self.header.grid(row=0, column=2, columnspan=1)
        self.box1_text.grid(row=3, column=1, sticky="w")
        self.box2_text.grid(row=4, column=1, sticky="w")
        self.box3_text.grid(row=5, column=1, sticky="w")
        self.quality_dropdown.grid(row=5, column=2, sticky="w")
        self.start_button.grid(row=6, column=2)
        self.progressbar_text.grid(row=7, column=2)
        self.progressbar.grid(row=8, column=2)

        self.fields = []
        for i in range(2):
            path_field = tk.Entry(self.root, width=50)
            path_field.grid(row=i + 3, column=2)
            browse_button = tk.Button(
                self.root,
                text="Browse...",
                command=lambda field_num=i: self.browse(self.fields, field_num),
            )
            browse_button.grid(row=i + 3, column=3)
            self.fields.append(path_field)

    def update_progressbar(self):
        self.progressbar.update()

    def post_conversion_dialogue(self, num_of_images, num_of_non_images):
        if num_of_images == 0:
            tk.messagebox.showerror("Error", "No images were found in source folder.")
            return False
        elif num_of_non_images > 0:
            return tk.messagebox.askyesno(
                "Copy non-images?",
                f"""{num_of_images} files were successfully converted.
{num_of_non_images} files could not be converted. they are most likely not images.
Copy non-images to destination folder?""",
            )
        else:
            tk.messagebox.showinfo(
                "Conversion complete!",
                f"{num_of_images} files were successfully converted.",
            )
            return False


if __name__ == "__main__":
    gui = Gui()
    gui.build_window()
    gui.root.mainloop()
