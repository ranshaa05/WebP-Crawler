import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog #tkinter bug
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
        self.start_button = None
        self.quality_lossless_button = None
        self.quality_dropdown = None
        self.fields = None
        self.app_logic = converter.AppLogic()

        self.build_window()

        self.root.mainloop()

    def check_params(self, src_path, dst_path, quality):
        if src_path == "" or dst_path == "\\":                          #check if paths are usable
            tk.messagebox.showerror("Error", "You must enter a source and destination path.")
        elif src_path + "\\" == dst_path:
            tk.messagebox.showerror("Error", "Source and destination folders cannot be the same.")
        elif not path.exists(src_path):
            tk.messagebox.showerror("Error", "Source folder does not exist.\nPlease select a different folder.")
        elif not path.exists(dst_path):
            tk.messagebox.showerror("Error", "Destination folder does not exist.\nPlease select a different folder.")
        elif path.isdir(dst_path + path.basename(src_path)):    #TODO: maybe add an option to override current folder?
            tk.messagebox.showerror("Error", f'Destination folder already has a folder named "{path.basename(src_path)}" in it.\nPlease select a different destination folder.')
        
        elif quality == "Select...":                        #check if quality value is set
            tk.messagebox.showinfo("Info", "Please select a quality value.")

        else:
            return src_path, dst_path, quality

    def convert(self):
        src_path = self.fields[0].get()
        dst_path = self.fields[1].get() + "\\"
        quality = self.quality_dropdown.get()
        
        if self.check_params(src_path, dst_path, quality):
            self.app_logic.create_folder_tree(src_path, dst_path)
            self.app_logic.convert(src_path, dst_path, quality)


    def browse(self, path_field, field_num):
       path = tk.filedialog.askdirectory(mustexist=True, title="Select Destination Folder").replace("/", "\\")
       path_field[field_num].delete(0, tk.END)
       path_field[field_num].insert(0, path)

    def build_window(self):
        self.header = tk.Label(self.root, text="Enter path:")
        self.box1_text = tk.Label(self.root, text="Source folder:")
        self.box2_text = tk.Label(self.root, text="Destination folder:")
        self.start_button = tk.Button(self.root, text="Start", command=self.convert)
        self.box3_text = tk.Label(self.root, text="Quality:")
        self.quality_lossless_button = tk.Button(self.root, text="Lossless", command=lambda: dropdown_text.set("Lossless"))
        dropdown_text = tk.StringVar(self.root)
        dropdown_text.set("Select...")
        self.quality_dropdown = ttk.Combobox(self.root, textvariable=dropdown_text, state="readonly", width=15)
        self.quality_dropdown["values"] = ("Select...", *[str(i) for i in range(100, -1, -1)])

        self.header.grid(row=0, column=2, columnspan=1)
        self.box1_text.grid(row=3, column=1, sticky="w")
        self.box2_text.grid(row=4, column=1, sticky="w")
        self.box3_text.grid(row=5, column=1, sticky="w")
        self.quality_dropdown.grid(row=5, column=2, sticky="w")
        self.quality_lossless_button.grid(row=5, column=2)
        self.start_button.grid(row=6, column=2)
        

        self.fields = []
        for i in range(2):
            path_field = tk.Entry(self.root, width=50)
            path_field.grid(row=i+3, column=2)
            browse_button = tk.Button(self.root, text="Browse...", command=lambda field_num=i: self.browse(self.fields, field_num))
            browse_button.grid(row=i+3, column=3)
            self.fields.append(path_field)


if __name__ == '__main__':
    Gui()
