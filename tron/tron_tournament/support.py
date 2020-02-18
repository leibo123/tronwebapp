########################### support.py #############################


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Player action timed out.")
