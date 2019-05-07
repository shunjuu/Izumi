class DistributionPrints:
    """
    This class stores the various print staetments uesd by Encode itself
    """    

    def __init__(self, colors):
        """
        Params:
            colors - prnit_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC 
        prefix = "[Distribution] "

        distribution_color = colors.GREEN

        self.WORKER_SPAWN = prefix + "Spawning " + distribution_color + \
            "{}" + endc + " thread(s)"

        self.NEW_REQUEST = prefix + distribution_color + "New request received." + endc

        self.JOB_COMPLETE = prefix + distribution_color + "Job completed." + endc