import tkinter as tk
from tkinter import filedialog #tkinter bug
import converter


class Gui:
    def __init__(self, root=None):
        if not root:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title("All To webp")
        self.root.geometry("480x100")

        self.header = None
        self.box1_text = None
        self.box2_text = None
        self.start_button = None
        self.fields = None
        self.new_button = tk.Button(text='do something', command=self.convert)
        self.app_logic = converter.AppLogic()

        self.build_window()

        self.root.mainloop()

    def convert(self):
        src_path = self.fields[0].get()
        dst_path = self.fields[1].get() + "\\"
        #quality = self.fields[1].get()


        self.app_logic.create_folder_tree(src_path, dst_path)
        self.app_logic.convert(src_path, dst_path, "100")

    def browse(self, path_field, field_num):
       path = tk.filedialog.askdirectory(mustexist=True, title="Select Destination Folder").replace("/", "\\")
       path_field[field_num].delete(0, tk.END)
       path_field[field_num].insert(0, path)

    def build_window(self):
        self.header = tk.Label(self.root, text="Enter path:")
        self.box1_text = tk.Label(self.root, text="Source folder:")
        self.box2_text = tk.Label(self.root, text="Destination folder:")


        self.start_button = tk.Button(self.root, text="Start", command=self.convert)

        self.header.grid(row=0, column=2, columnspan=1)

        self.box1_text.grid(row=3, column=1)
        self.box2_text.grid(row=4, column=1)
        self.start_button.grid(row=5, column=1)

        self.fields = []
        for i in range(2):
            path_field = tk.Entry(self.root, width=50)
            path_field.grid(row=i+3, column=2)
            browse_button = tk.Button(self.root, text="Browse...", command=lambda field_num=i: self.browse(self.fields, field_num))
            browse_button.grid(row=i+3, column=3)
            self.fields.append(path_field)


if __name__ == '__main__':
    Gui()
