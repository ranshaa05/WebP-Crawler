import sys
from pathlib import Path

from gui import Gui


def get_resource_path(relative_path):
    """Get the absolute path to a resource in a way that works for development and for PyInstaller/Nuitka bundles."""
    try:
        # PyInstaller/Nuitka creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent

    return Path(base_path) / relative_path


if __name__ == "__main__":
    icon_path = get_resource_path("icon.ico")
    gui = Gui(icon_path)
    gui.root.mainloop()    gui.root.mainloop()