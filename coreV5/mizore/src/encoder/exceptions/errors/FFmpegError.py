"""
For errors that occur in ffmpeg operations
Message is provided by dev, output is for ffmpeg output
"""

from src.encoder.exceptions.EncoderException import EncoderException #pylint: disable=import-error

class FFmpegError(EncoderException):
    def __init__(self, message: str, output: str):
        self.message = message
        self.output = output