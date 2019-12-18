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

class Job:

    def __init__(self, show: str = None, episode: str = None, filesize: int = -1, sub: str = None) -> None:
        self._show = show
        self._episode = episode
        self._filesize = filesize
        self._sub = sub

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
