"""
Constant class for storing encoder configurations
"""

from typing import Dict, List

class EncoderConfigStore:

    def __init__(self, dl_srcs, dl_rcf, up_dest, up_rcf, edpts):
        """
        dl_srcs: List[str]: List of downloading sources
        dl_rcf: str: Downloading rclone flags
        up_dest: List[str]: List of uploading destinations
        up_rcf: str: Uploading rclone flags
        edpts: List[Dict[str, str,]]: Endpoints for POSTing
        """
        self._downloading_sources = dl_srcs
        self._downloading_rclone_flags = dl_rcf
        self._uploading_destinations = up_dest
        self._uploading_rclone_flags = up_rcf
        self._endpoints = edpts

    @property
    def downloading_sources(self) -> List[str]:
        return self._downloading_sources

    @property
    def downloading_rclone_flags(self) -> str:
        return self._downloading_rclone_flags

    @property
    def uploading_destinations(self) -> List[str]:
        return self._uploading_destinations

    @property
    def uploading_rclone_flags(self) -> str:
        return self._uploading_rclone_flags

    @property
    def endpoints(self) -> List[Dict[str, str]]:
        return self._endpoints