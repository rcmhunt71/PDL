"""
  Utility for timing routines as a decorator.
  Could have used time-it or other modules, but for fun and experience with writing decorators,
  opted to write my own.
"""

import time
from typing import Callable

import PDL.logger.logger as logger

BASE = 10.0
PRECISION = 4
MULTIPLIER = pow(BASE, PRECISION)

LOG = logger.Logger()


def measure_elapsed_time(event: str, test: bool = False) -> Callable:
    """
    Decorator for measuring the execution time of a specific call

    :param event: (str) Name or keyword identifier of event being measured
    :param test:  (bool) If True, returns the time elapsed as part of output.
                    This assumes f() does not return anything, otherwise the
                    output needs to be reworked, or the msg will overwrite the
                    return value of f().

    :return: executed function return

    """
    def wrap(func):
        def wrapped_func(*args, **kwargs):
            start = time.time()
            ret_val = func(*args, **kwargs)
            elapsed = int((time.time() - start) * MULTIPLIER) / MULTIPLIER
            msg = f"[{event.upper()}]: Elapsed Time: {elapsed} s"
            LOG.info(msg)
            if test:
                return elapsed
            return ret_val
        return wrapped_func
    return wrap
