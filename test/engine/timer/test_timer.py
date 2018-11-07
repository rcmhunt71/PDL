import sys
import time

from PDL.engine.timer.timer import measure_elapsed_time
from nose.plugins.capture import Capture

from nose.tools import assert_equals, raises


@measure_elapsed_time('test', test=True)
def my_func(delay):
    time.sleep(delay)


class TestTimer(object):

    def test_timer(self):
        delay = 1
        out = my_func(delay)
        assert_equals(int(out), delay)
