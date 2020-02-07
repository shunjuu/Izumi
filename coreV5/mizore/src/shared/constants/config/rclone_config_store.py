# pylint: disable=import-error
"""
Stores Rclone config objects to pass as part of jobs.
Passing this enables fully independent works.
"""

class RcloneConfigStore:

        def __init__(self, content: str):
            self._content = content
            self._file = str()

        @property
        def content(self):
            return self._content
