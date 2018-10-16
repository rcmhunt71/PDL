import inspect
import os

from PDL.configuration.properties.app_cfg import (
    Config, ConfigSectionDoesNotExist, OptionDoesNotExist,
    CannotCastValueToType)

from nose.tools import assert_equals, assert_true, raises


class TestPropertiesConfig(object):

    VALID_SECTIONS = ['setup', 'test', 'teardown']
    VALID_OPTIONS = (
        'teardown', ["report", "resources", "clear_resources", "abort_on_fail"])
    INVALID_SECTION = 'section_does_not_exist'
    INVALID_OPTION = 'option_does_not_exist'
    VALID_SECTION_AND_ITEM_STR = ('teardown', 'report', '"results.xml"')
    VALID_SECTION_AND_ITEM_INT = ('setup', 'testcases', 10)
    VALID_SECTION_AND_ITEM_BOOL = ('teardown', 'clear_resources', True)
    VALID_SECTION_AND_ITEM_FLOAT = ('test', 'averages', 5.5)
    VALID_SECTION_AND_ITEM_LIST = (
        'teardown', 'resources', ['Nova', 'Neutron', 'Cinder'])

    @classmethod
    def setup_class(cls):
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        cls.cfg_file = '{0}.data'.format(os.path.splitext(filename)[0])
        cls.config = Config(cfg_file=cls.cfg_file)

    def _print_config_file(self):
        with open(self.cfg_file) as CFG:
            lines = CFG.readlines()
        print("CFG FILE ({location}):\n\t{contents}".format(
            location=self.cfg_file, contents='\t'.join(lines)))

    def test_get_sections(self):
        expected_sections = ['setup', 'test', 'teardown']
        self._print_config_file()
        assert_equals(self.config.get_sections(), expected_sections)

    def test_get_options_populated(self):
        actual_options = self.config.get_options(section=self.VALID_OPTIONS[0])
        assert_equals(sorted(actual_options), sorted(self.VALID_OPTIONS[1]))

    @raises(ConfigSectionDoesNotExist)
    def test_get_options_non_existent_section(self):
        expected_options = list()
        actual_options = self.config.get_options(section=self.INVALID_SECTION)
        assert_equals(sorted(actual_options), sorted(expected_options))

    @raises(ConfigSectionDoesNotExist)
    def test_get_option_non_existent_section(self):
        expected_option = None
        actual_option = self.config.get_option(
            section=self.INVALID_SECTION, option=self.INVALID_OPTION)
        assert_equals(actual_option, expected_option)

    @raises(OptionDoesNotExist)
    def test_get_option_non_existent_option(self):
        expected_option = None
        actual_option = self.config.get_option(
            section=self.VALID_SECTIONS[-1], option=self.INVALID_OPTION)
        assert_equals(actual_option, expected_option)

    def test_get_option_valid_section_valid_option(self):
        data = self.VALID_SECTION_AND_ITEM_STR
        expected_value = data[2]
        actual_value = self.config.get_option(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, str))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_int(self):
        data = self.VALID_SECTION_AND_ITEM_INT
        expected_value = data[2]
        actual_value = self.config.get_int(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, int))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_boolean(self):
        data = self.VALID_SECTION_AND_ITEM_BOOL
        expected_value = data[2]
        actual_value = self.config.get_boolean(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, bool))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_float(self):
        data = self.VALID_SECTION_AND_ITEM_FLOAT
        expected_value = data[2]
        actual_value = self.config.get_float(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, float))
        assert_equals(actual_value, expected_value)

    @raises(CannotCastValueToType)
    def test_get_option_valid_section_valid_str_illegal_cast_float(self):
        data = self.VALID_SECTION_AND_ITEM_STR
        expected_value = data[2]
        actual_value = self.config.get_float(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, float))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_list(self):
        data = self.VALID_SECTION_AND_ITEM_LIST
        expected_value = data[2]
        actual_value = self.config.get_list(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, list))
        assert_equals(actual_value, expected_value)
