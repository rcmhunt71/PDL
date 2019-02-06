from PDL.logger.logger import Logger
from nose.tools import assert_equals


class TestLogger(object):

    """
    Focus is primarily on cascading default values across logging contexts
    (children) and the logic associated with reporting and maintaining the
    child loggers.
    """

    def test_if_all_logging_children_and_levels_are_reported(self):
        # Validate logging children are reported correctly

        log_1_level = Logger.INFO
        root_level = Logger.DEBUG

        # Set up the loggers
        log_1 = Logger(default_level=log_1_level, test_name='log_1')
        log_2 = Logger(test_name='log_2')
        root = Logger(default_level=root_level, set_root=True)

        # Record the expected names and levels
        expected_names = {log_1.name, log_2.name, root.name}
        expected_log_levels = {log_1.name: root_level,
                               log_2.name: root_level,
                               root.name: root_level}

        # Get the actual logger info
        children = root._list_loggers()
        actual_child_names = set([name for name, level in children])
        actual_log_levels = dict([(name, level) for name, level in children])

        # Print state (for debugging on failure)
        print(root.list_loggers())
        print(f"\nACTUAL NAMES: {actual_child_names}")
        print(f"\nEXPECTED NAMES: {expected_names}")
        print(f"\nINTERSECTION: {actual_child_names.intersection(expected_names)}")

        # The length of the set intersection should be the same length as
        # the expected names.
        assert_equals(len(actual_child_names.intersection(expected_names)),
                      len(expected_names))

        # Check the logging level for the actual level matches the
        # expected level.
        for name, actual_level in actual_log_levels.items():
            expected_level = expected_log_levels.get(name, None)

            if expected_level is not None:
                expected_level = Logger.VAL_TO_STR[expected_level].upper()
                print(f"\nName: {name}\nExpected Value: {expected_level}"
                      f"\nActual Value: {actual_level}")

                assert_equals(actual_level, expected_level)

    def test_if_dotted_path_is_correct(self):

        # This should not change unless the logger test file is moved or path
        # renamed.
        expected_module_path = 'test.logger.test_logger'

        log_1 = Logger(added_depth=-2)
        reported_module_path = log_1._get_module_name()
        print(f"Module Name: {reported_module_path}")
        assert_equals(expected_module_path, reported_module_path)
