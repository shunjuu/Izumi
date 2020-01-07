"""
Request class for each kind of REST request

Request type json:
{
    "show": $SHOW_NAME,
    "episode": $EPISODE_NAME,
    "filesize" : $FILE_SIZE,
    "sub": $SUB_TYPE,
}
"""

from enum import Enum

class JobType(Enum):
    DISTRIBUTE = "distribute"
    ENCODE = "encode"
    NOTIFY = "notify"

class Job:

    def __init__(self, show: str = None, episode: str = None, filesize: int = -1, sub: str = None, jobtype: JobType = None):
        self._show = show
        self._episode = episode
        self._filesize = filesize
        self._sub = sub
        self._jobtype = jobtype

    @property
    def show(self) -> str:
        return self._show

    @property
    def episode(self) -> str:
        return self._episode

    @property
    def filesize(self) -> int:
        return self._filesize

    @property
    def sub(self) -> str:
        return self._sub

    @property
    def jobtype(self) -> JobType:
        return self._jobtype