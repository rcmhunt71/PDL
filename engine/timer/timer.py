import time

import PDL.logger.logger as logger

PRECISION = 4
MULTIPLIER = pow(10.0, PRECISION)

log = logger.Logger()


def measure_elapsed_time(event, test=False):
    """
    Decorator for measuring the execution time of a specific call

    :param event: (str) Name or keyword identifier of event being measured
    :param test:  (bool) If True, returns the time elapsed as part of output.
                    This assumes f() does not return anything, otherwise the
                    output needs to be reworked, or the msg will overwrite the
                    return value of f().

    :return: executed function return

    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            start = time.time()
            f(*args, **kwargs)
            elapsed = int((time.time() - start) * MULTIPLIER) / MULTIPLIER
            msg = ("[{event}]: Elapsed Time: {elapsed} s".format(
                elapsed=elapsed, event=event.upper()))
            log.info(msg)
            if test:
                return elapsed
        return wrapped_f
    return wrap
