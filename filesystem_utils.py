from pathlib import Path

from PIL import Image

# Supported image formats
REGISTERED_EXTENSIONS = {ext.lower() for ext in Image.registered_extensions()}

def create_folder_tree(src_path: Path, dst_path: Path):
    """Copy the source folder tree in the destination path."""

    if not dst_path.exists():
        dst_path.mkdir(parents=True, exist_ok=True)
    (dst_path / src_path.name).mkdir(parents=True, exist_ok=True)

    for item in src_path.rglob("*"):
        if item.is_dir():
            destination = dst_path / src_path.name / item.relative_to(src_path)
            destination.mkdir(parents=True, exist_ok=True)

def make_destination_folders(src_path, dst_path, include_subfolders):
    if include_subfolders:
        create_folder_tree(src_path, dst_path)
    else:
        (dst_path / src_path.name).mkdir(parents=True, exist_ok=True)

def detect_images(src_path, include_subfolders, f_ext):
    image_files = []
    non_image_files = []
    already_formatted_images = []

    if include_subfolders:
        files = src_path.rglob("*.*")
    else:
        files = src_path.glob("*.*")

    for file in files:
        extension = file.suffix
        if extension.lower() == f".{f_ext}":
            already_formatted_images.append(file)
        if extension.lower() in REGISTERED_EXTENSIONS:
            image_files.append(file)
        else:
            non_image_files.append(file)

    return image_files, non_image_files, already_formatted_images