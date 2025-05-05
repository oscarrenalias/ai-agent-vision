import os
from pathlib import Path


def get_uploads_folder():
    """
    Get the uploads folder path from the environment variable UPLOAD_FOLDER.
    If the environment variable is not set, raise a ValueError.
    """
    if os.getenv("UPLOAD_FOLDER") is None:
        # it's a big issue if this variable isn't set
        raise ValueError("UPLOAD_FOLDER cannot be empty")

    return Path.cwd() / os.getenv("UPLOAD_FOLDER")
