"""
Helps do some basic filepath operations (not moving files)
"""

import os.path

from pathlib import Path

# Important: This file should not have any nonstandard dependencies

class PathUtils:

    @staticmethod
    def clean_directory_path(path: str) -> str:
        """Make sure directory paths passed in end with '/'"""
        if not path.endswith("/"):
            return path + "/"
        return path
    
    @staticmethod
    def modify_flask_route(path: str) -> str:
        """Make sure the passed in flask route starts with a '/'"""
        if not path.startswith("/"):
            return "/" + path
        return path
    
    @staticmethod
    def abspath(path: str) -> str:
        """OS.Abspath"""
        return os.path.abspath(path)
    
    @staticmethod
    def abspath_root() -> str:
        """Returns the root path of the project"""
        # Isn't coding just so fun?!
        return PathUtils.clean_directory_path(Path(__file__).parent.parent.parent.parent.parent.absolute().as_posix())