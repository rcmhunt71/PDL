import time

import PDL.logger.logger as logger

PRECISION = 4
MULTIPLIER = pow(10.0, PRECISION)

log = logger.Logger()


def measure_elapsed_time(event):
    """
    Decorator for measuring the execution time of a specific call

    :param event: Name or keyword identifier of event being measured

    :return: executed function return

    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            start = time.time()
            f(*args, **kwargs)
            elapsed = str(int((time.time() - start) * MULTIPLIER) / MULTIPLIER)
            log.info("[{event}]: Elapsed Time: {elapsed} s".format(
                elapsed=elapsed, event=event.upper()))
        return wrapped_f
    return wrap
