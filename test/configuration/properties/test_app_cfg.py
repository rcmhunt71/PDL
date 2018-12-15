import inspect
import os
from configparser import NoSectionError, NoOptionError

from PDL.configuration.properties.app_cfg import (
    AppConfig, ConfigSectionDoesNotExist, CfgFileDoesNotExist)
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
    INVALID_SECTION_AND_VALID_OPTION_LIST = (
        INVALID_SECTION, 'resources', ['Nova', 'Neutron', 'Cinder'])
    VALID_SECTION_AND_INVALID_OPTION_LIST = (
        'teardown', INVALID_OPTION, ['Nova', 'Neutron', 'Cinder'])
    INVALID_CFG_FILE = 'DNE.txt'

    def setup(self):
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.cfg_file = '{0}.data'.format(os.path.splitext(filename)[0])
        self.config = AppConfig(cfg_file=self.cfg_file, test=True)

    def _print_config_file(self):
        with open(self.cfg_file) as CFG:
            lines = CFG.readlines()
        print("CFG FILE ({location}):\n\t{contents}".format(
            location=self.cfg_file, contents='\t'.join(lines)))

    def test_app_config_init(self):
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.cfg_file = '{0}.data'.format(os.path.splitext(filename)[0])
        self.config = AppConfig(cfg_file=self.cfg_file, test=False)

        assert self.config is not None
        assert sorted(self.config.sections()) == sorted(self.VALID_SECTIONS)

    @raises(CfgFileDoesNotExist)
    def test_if_missing_cfg_file_for_init_raises_error(self):
        AppConfig(cfg_file=self.INVALID_CFG_FILE, test=False)

    def test_get_sections(self):
        expected_sections = ['setup', 'test', 'teardown']
        self._print_config_file()
        assert_equals(self.config.sections(), expected_sections)

    def test_get_options_populated(self):
        actual_options = self.config.get_options(section=self.VALID_OPTIONS[0])
        assert_equals(sorted(actual_options), sorted(self.VALID_OPTIONS[1]))

    @raises(ConfigSectionDoesNotExist)
    def test_get_options_non_existent_section(self):
        self.config.get_options(section=self.INVALID_SECTION)

    @raises(NoSectionError)
    def test_get_option_non_existent_section(self):
        self.config.get(
            section=self.INVALID_SECTION, option=self.INVALID_OPTION)

    @raises(NoOptionError)
    def test_get_option_non_existent_option(self):
        self.config.get(
            section=self.VALID_SECTIONS[-1], option=self.INVALID_OPTION)

    def test_get_option_valid_section_valid_option(self):
        data = self.VALID_SECTION_AND_ITEM_STR
        expected_value = data[2]
        actual_value = self.config.get(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, str))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_int(self):
        data = self.VALID_SECTION_AND_ITEM_INT
        expected_value = data[2]
        actual_value = self.config.getint(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, int))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_boolean(self):
        data = self.VALID_SECTION_AND_ITEM_BOOL
        expected_value = data[2]
        actual_value = self.config.getboolean(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, bool))
        assert_equals(actual_value, expected_value)

    def test_get_option_valid_section_valid_float(self):
        data = self.VALID_SECTION_AND_ITEM_FLOAT
        expected_value = data[2]
        actual_value = self.config.getfloat(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, float))
        assert_equals(actual_value, expected_value)

    @raises(ValueError)
    def test_get_option_valid_section_valid_str_illegal_cast_float(self):
        data = self.VALID_SECTION_AND_ITEM_STR
        self.config.getfloat(section=data[0], option=data[1])

    def test_get_option_valid_section_valid_list(self):
        data = self.VALID_SECTION_AND_ITEM_LIST
        expected_value = data[2]
        actual_value = self.config.get_list(
            section=data[0], option=data[1])
        assert_true(isinstance(actual_value, list))
        assert_equals(actual_value, expected_value)

    @raises(NoSectionError)
    def test_get_option_invalid_section_valid_option_valid_list(self):
        data = self.INVALID_SECTION_AND_VALID_OPTION_LIST
        self.config.get_list(section=data[0], option=data[1])

    @raises(NoOptionError)
    def test_get_option_valid_section_invalid_option_valid_list(self):
        data = self.VALID_SECTION_AND_INVALID_OPTION_LIST
        self.config.get_list(section=data[0], option=data[1])
