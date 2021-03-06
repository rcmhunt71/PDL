import copy
from typing import NoReturn, List

from PDL.configuration.cli.args import CLIArgs, ArgSubmodules, ArgOptions
from nose.tools import raises, assert_equals, assert_false, assert_true


class TestCommandLine(object):

    MODULES = ArgSubmodules.get_const_names()

    def test_if_debug_flag_is_set(self):
        # Validate debug flag is reported as set.

        attr = ArgOptions.DEBUG
        cli_args = [self._build_longword_option(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_debug_flag_is_not_set(self):
        # Validate debug flag is reported as NOT SET.

        attr = ArgOptions.DEBUG
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_dryrun_flag_is_set(self):
        # Validate dry-run flag is reported as set.

        attr = ArgOptions.DRY_RUN
        cli_args = [self._build_longword_option(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_dryrun_flag_is_not_set(self):
        # Validate debug flag is reported as NOT SET.

        attr = ArgOptions.DRY_RUN
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_command_attribute_is_set_to_submenu(self):
        # Test if the CLIArgs.command contains the name of the correct submenu.

        attr = ArgOptions.COMMAND
        designator = ArgSubmodules.DOWNLOAD

        cli = CLIArgs(test_args_list=[designator,
                                      "www.foo.com/this/is/my/utl.html"])
        attribute = getattr(cli.args, attr)
        print(f"{attr} ATTRIBUTE: {attribute}")
        assert_equals(attribute, designator)

# --------- Improper CLI Argument Sets -------------

    @raises(SystemExit)
    def test_if_app_cfg_option_without_file_specified(self):
        # Test if cfg option throws error if file is not specified.
        # Proper arg list: --cfg <filespec>
        # Actual arg list: --cfg

        attr = ArgOptions.CFG
        CLIArgs(test_args_list=[self._build_longword_option(attr)])

    @raises(SystemExit)
    def test_if_engine_cfg_option_without_file_specified(self):
        # Test if cfg option throws error if file is not specified.
        # Proper arg list: --engine <filespec>
        # Actual arg list: --engine

        attr = ArgOptions.ENGINE
        CLIArgs(test_args_list=[self._build_longword_option(attr)])

    @raises(SystemExit)
    def test_if_image_without_filespec_raises_error(self):
        # Test if image sub option throws error if no image is specified.
        # Proper arg list: info image <filespec>
        # Actual arg list: info image

        attr = ArgOptions.IMAGE
        CLIArgs(test_args_list=[ArgSubmodules.INFO,
                                self._build_longword_option(attr)])

    @raises(SystemExit)
    def test_if_db_sync_and_records_are_mutually_exclusive(self):
        # Test if db --sync and --records are mutually exclusive.

        attr = [ArgOptions.SYNC, ArgOptions.RECORDS]
        CLIArgs(test_args_list=[self._build_longword_option(attr[0]),
                                self._build_longword_option(attr[1])])

    def test_if_db_sync_option_works_alone(self):
        # Test if db --sync option is accepted without arguments.

        attr = ArgOptions.SYNC
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(
            test_args_list=[designator, self._build_longword_option(attr)])
        value = getattr(cli.args, attr)
        print(f"{attr} ATTRIBUTE: {value}")
        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        assert_equals(getattr(cli.args, attr), True)

    def test_if_db_detail_option_is_stored(self):
        # Test if db --detail is stored correctly.

        attr = ArgOptions.DETAILS
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(test_args_list=[designator,
                                      self._build_longword_option(attr)])
        value = getattr(cli.args, attr)
        print(f"{attr} ATTRIBUTE: {value}")
        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        assert_equals(getattr(cli.args, attr), True)

    def test_if_db_record_record_and_details_options_are_stored(self):
        # Test if db --records --details is accepted.
        attributes = [ArgOptions.RECORDS, ArgOptions.DETAILS]
        designator = ArgSubmodules.DATABASE

        args = [designator]
        args.extend([f'--{attr}' for attr in attributes])
        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print(f"{attr} ATTRIBUTE: {value}")
            assert_equals(getattr(cli.args, attr), True)

    def test_if_db_records_with_details_and_filespec_options_is_stored(self):
        # Test if db --records --filespec_<filespec> --details is stored.
        filespec_opt = ArgOptions.FILE_SPEC
        filespec = "'./*.png'"
        attributes = ['records', 'details', filespec_opt]
        designator = ArgSubmodules.DATABASE
        args = [designator]
        args.extend([self._build_longword_option(filespec_opt), filespec])
        args.extend([self._build_longword_option(attr) for attr in attributes if
                     attr != filespec_opt])

        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print(f"{attr.upper()} ATTRIBUTE: {attr} = {value}")
            expected = True
            if attr == filespec_opt:
                expected = filespec
            assert_equals(getattr(cli.args, attr), expected)

    @raises(SystemExit)
    def test_if_db_record_details_and_filespec_opts_wo_filespecs_errors(self):
        # Test if db --records --details --filespec raises an error if the
        # filespec does not have a specifier (e.g. *.jpg)

        file_spec = "'./*.png'"
        attributes = [ArgOptions.RECORDS, ArgOptions.DETAILS,
                      ArgOptions.FILE_SPEC]
        designator = ArgSubmodules.DATABASE
        args = [designator]
        args.extend([self._build_longword_option(attr) for attr in attributes])

        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print(f"{attr} ATTRIBUTE: {value}")
            expected = True
            if attr == ArgOptions.FILE_SPEC:
                expected = file_spec
            assert_equals(getattr(cli.args, attr), expected)

    @raises(SystemExit)
    def test_if_image_without_info_designator_wo_filespec_raises_error(self):
        # Test if image suboption without image filespec raises an error
        # Proper arg list: <designator> <option> <value>
        # Actual arg list: <option> <value>

        attr = ArgOptions.IMAGE
        cli = CLIArgs(test_args_list=[self._build_longword_option(attr),
                                      'foo.tmp'])

        # Should cause error (sysExit)
        getattr(cli.args, attr)

    @raises(SystemExit)
    def test_if_invalid_designator_raises_error(self):
        # Verify an invalid (unrecognized) designator raises an error.
        # Proper arg list: <known_designator>
        # Actual arg list: <unknown_designator>

        designator = 'FOO'
        CLIArgs(test_args_list=[designator])

    def test__get_module_names(self):
        names = dict([(mod, getattr(ArgSubmodules, mod)) for mod in self.MODULES])
        name_list = ArgSubmodules.get_const_names()
        assert_equals(set(name_list), set(names.keys()))

    def test__get_module_values(self):
        names = dict([(mod, getattr(ArgSubmodules, mod)) for mod in self.MODULES])
        value_list = ArgSubmodules.get_const_values()
        assert_equals(set(value_list), set(names.values()))

    def test_get_module_names(self):
        names = dict([(mod, getattr(ArgSubmodules, mod)) for mod in self.MODULES])
        name_list = CLIArgs.get_module_names()
        assert_equals(set(name_list), set(names.values()))

    def test_get_invalid_shortcut(self):
        option = CLIArgs.get_shortcut(option='8')
        assert_equals(option, '')

    @staticmethod
    def _verify_boolean_response(attr: str, cli_args: List[str], bool_expectation: bool) -> NoReturn:
        """
        Sets up CLIArgs object with provided args, verify the boolean response
        is correct, based on the boolean expectation.

        :param attr: Option to test (created as an attribute of CLIArgs)
        :param cli_args: CLI arguments
        :param bool_expectation: Boolean T/F
        :return: assert or pass

        """
        cli = CLIArgs(test_args_list=cli_args)
        attribute = getattr(cli.args, attr)
        print(f"{attr} ATTRIBUTE: {attribute}")
        if bool_expectation:
            assert_true(attribute)
        else:
            assert_false(attribute)

    @staticmethod
    def _build_longword_option(option: str) -> str:
        return f'--{option}'

    def test_get_args_str(self):
        args, options, flags = self._build_args_for_args_output_tests()
        cli = CLIArgs(test_args_list=args)

        output = cli.get_args_str()
        print(f"Output: {output}")

        for option in options:
            assert option in output

    def test_get_opt_args_states(self):
        args, options, flags = self._build_args_for_args_output_tests()
        cli = CLIArgs(test_args_list=args)
        output = cli.get_opt_args_states()
        print(f"Output: {output}")

        for option in flags:
            bool_val = "ENABLED" if getattr(cli.args, option) else "DISABLED"
            assert f"{option} {bool_val}" in output

    def _build_args_for_args_output_tests(self):
        filespec_opt = ArgOptions.FILE_SPEC
        filespec = "'./*.png'"
        attributes = ['records', 'details', filespec_opt]
        designator = ArgSubmodules.DATABASE

        flags = copy.copy(CLIArgs.FLAGS[ArgSubmodules.GENERAL])
        flags.extend(CLIArgs.FLAGS[designator])

        options = [filespec_opt, filespec, designator]
        options.extend(attributes)
        options.extend(flags)
        args = [designator]
        args.extend([self._build_longword_option(filespec_opt), filespec])
        args.extend([self._build_longword_option(attr) for attr in attributes if
                     attr != filespec_opt])
        return args, options, flags
