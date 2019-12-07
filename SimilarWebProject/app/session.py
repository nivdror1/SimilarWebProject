
THIRTY_MINUTES = 1800


class Session:

    def __init__(self, visitor, site, timestamp):
        self.visitor = visitor
        self.site = site
        self.start_timestamp = timestamp
        self.end_timestamp = timestamp

    def update_timestamp(self, current_timestamp):
        """
        update the session end timestamp
        :param current_timestamp: The page view timestamp
        """
        self.end_timestamp = current_timestamp

    def same_session(self, current_timestamp):
        """
        Check if the current page view is in the same session
        :param current_timestamp: The page view timestamp
        :return: Boolean
        """
        return int(current_timestamp) - int(self.end_timestamp) <= THIRTY_MINUTES

    def get_length(self):
        """
        get the length of the session
        :return: The length of the session
        """
        return int(self.end_timestamp) - int(self.start_timestamp)

    def __repr__(self):
        return 'visitor is {}, site is {}, start is {}, end is {}'.format(self.visitor, self.site, self.start_timestamp, self.end_timestamp)