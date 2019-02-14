class EncodePrints:
    """
    This class stores the various print staetments uesd by Encode itself
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC 
        prefix = "[Encoder] "

        encode_color = colors.GREEN

        self.WORKER_SPAWN = prefix + "Spawning " + encode_color + \
            "{}" + endc + " thread(s)"

        self.NEW_REQUEST = prefix + encode_color + "New request received." + endc

        self.JOB_COMPLETE = prefix + encode_color + "Job completed." + endc