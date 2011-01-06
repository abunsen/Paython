class DataValidationError(Exception):
    """ Errors when data is corrupt, malformed or just plain wrong """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class MissingDataError(Exception):
    """ Errors when data is missing in developer API call """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class GatewayError(Exception):
    """ Errors returned from API Gateway """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class RequestError(Exception):
    """ Errors during the API Request """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
