class NotificationPrints:
    """
    This class stores all the various print statements used by Notifcation itself
    """

    def __init__(self, colors):
        """  
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[Notification] "

        notif_color = colors.GREEN
        self.WORKER_SPAWN = prefix + "Spawning " + notif_color + \
            "{}" + endc + " thread(s)"

        self.NEW_REQUEST = prefix + notif_color + "New request received." + endc

        self.JOB_COMPLETE = prefix + notif_color + "Job completed." + endc