
class H264StandardPrints:

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use varialbes
        endc = colors.ENDC 
        prefix = "[H264S] "

        self.FFMPEG_8_PATH = prefix + "Using ffmpeg-8bit from " + \
            colors.LMAGENTA + "{}" + endc

        self.FFMPEG_10_PATH = prefix + "Using ffmpeg-10bit from " + \
            colors.LMAGENTA + "{}" + endc

        # Encoding status
        self.ENCODE_START = prefix + "Starting encode of " + \
            colors.OKGREEN + "{}" + endc

        self.ENCODE_FINISH = prefix + "Finished encode of " + \
            colors.OKGREEN + "{}" + endc