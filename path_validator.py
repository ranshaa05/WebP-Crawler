from CTkMessagebox import CTkMessagebox


def check_paths(src_path, dst_path):
        """checks that the source and destination paths are valid and returns them if they are."""
        error_messages = {
            "empty": ("Error", "You must enter both source and destination paths."),
            "not_absolute": ("Error", "Source and destination paths must be absolute."),
            "same_path": (
                "Error",
                "Source and destination folders cannot be the same.",
            ),
            "src_not_exist": ("Error", "The source path does not exist."),
            "different_folder": (
                "Select a different folder.",
                "Please select a different destination folder.",
            ),
            "dst_in_src": (
                "Error",
                "Destination folder cannot be inside source folder.",
            ),
        }

        src_basename = src_path.name

        if str(src_path) == "." or str(dst_path) == ".":
            title, message = error_messages["empty"]
        elif not src_path.is_absolute() or not dst_path.is_absolute():
            title, message = error_messages["not_absolute"]
        elif not src_path.exists():
            title, message = error_messages["src_not_exist"]
        elif src_path == dst_path:
            title, message = error_messages["same_path"]

        elif dst_path.is_relative_to(src_path):
            title, message = error_messages["dst_in_src"]

        elif (dst_path / src_basename).is_dir():
            use_folder = CTkMessagebox(
                title="Destination folder already exists",
                message=f"Destination already contains folder '{src_basename}' inside it."
                "\nWould you like to use it anyway?",
                icon="question",
                option_1="Yes",
                option_2="No",
            )
            if use_folder.get() == "Yes":
                return True
            else:
                title, message = error_messages["different_folder"]
                print("Invalid parameters. No changes have been made.")
                return False

        else:
            return True

        CTkMessagebox(
            title=title,
            message=message,
            icon="cancel",
            sound=True,
        )
        print("Invalid parameters. No changes have been made.")
        return False        return False