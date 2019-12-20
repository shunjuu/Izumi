"""
Overatching exceptions for Rclone
"""

from src.shared.exceptions.SharedExceptions import SharedException #pylint: disable=import-error

class RcloneError(SharedException):
    """
    Errors that occur in rclone operations
    Message is provided by dev, output is for rclone output
    """
    def __init__(self, message: str, output: str, source: str, dest: str):
        self.message = message
        self.output = output
        self.source = source
        self.dest = dest

class RcloneUploadError(RcloneError):
    """When a file fails to be uploaded"""
    def __init__(self, message: str, output: str, source: str, dest: str):
        super().__init__(message, output, source, dest)

class RcloneDownloadError(RcloneError):
    """When a file fails to download"""
    def __init__(self, message: str, output: str, source: str, dest: str):
        super().__init__(message, output, source, dest)
    
class RcloneDownloadNotFoundError(RcloneError):
    """When a file requested for download isn't found"""
    def __init__(self, message: str, output: str, source: str, dest: str):
        super().__init__(message, output, source, dest)

class RcloneLSJsonError(RcloneError):
    """When the rclone lsjson command fails"""
    def __init__(self, message: str, output: str, source: str, dest: str):
        super().__init__(message, output, source, dest)
