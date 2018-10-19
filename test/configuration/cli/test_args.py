from PDL.configuration.cli.args import CLIArgs, ArgSubmodules, ArgOptions

from nose.tools import raises, assert_equals, assert_false, assert_true


class TestCommandLine(object):

    # TODO: Add test case descriptions

    def test_if_debug_flag_is_set(self):
        """
        Validate debug flag is reported as set.
        """
        attr = ArgOptions.DEBUG
        cli_args = ['--{0}'.format(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_debug_flag_is_not_set(self):
        """
        Validate debug flag is reported as NOT SET.
        """
        attr = ArgOptions.DEBUG
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_dryrun_flag_is_set(self):
        """
        Validate dryrun flag is reported as set.
        """
        attr = ArgOptions.DRYRUN
        cli_args = ['--{0}'.format(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_if_dryrun_flag_is_not_set(self):
        """
        Validate debug flag is reported as NOT SET.
        """
        attr = ArgOptions.DRYRUN
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._verify_boolean_response(
            attr=attr, cli_args=cli_args, bool_expectation=expectation)

    @staticmethod
    def _verify_boolean_response(attr, cli_args, bool_expectation):
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
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        if bool_expectation:
            assert_true(attribute)
        else:
            assert_false(attribute)

    def test_if_command_attribute_is_set_to_submenu(self):
        """
        Test if the CLIArgs.command contains the name of the correct submenu.
        """
        attr = ArgOptions.COMMAND
        designator = ArgSubmodules.DOWNLOAD

        cli = CLIArgs(test_args_list=[designator,
                                      "www.foo.com/this/is/my/utl.html"])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        assert_equals(attribute, designator)

# --------- Improper CLI Argument Sets -------------

    @raises(SystemExit)
    def test_if_cfg_option_without_file_specified(self):
        """
        Test if cfg option throws error if file is not specified.
        """
        # Proper arg list: --cfg <filespec>
        # Actual arg list: --cfg

        attr = ArgOptions.CFG
        cli = CLIArgs(test_args_list=['--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_if_image_without_filespec_raises_error(self):
        """
        Test if image sub option throws error if no image is specified.
        """
        # Proper arg list: info image <filespec>
        # Actual arg list: info image

        attr = ArgOptions.IMAGE
        cli = CLIArgs(test_args_list=[ArgSubmodules.INFO, '--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_if_db_sync_and_records_are_mutually_exclusive(self):
        """
        Test if db --sync and --records are mutually exclusive.
        """
        attr = [ArgOptions.SYNC, ArgOptions.RECORDS]
        cli = CLIArgs(test_args_list=['--{0}'.format(attr[0]), '--{0}'.format(attr[1])])
        for attribute in attr:
            value = getattr(cli.args, attribute)
            print("{attr} ATTRIBUTE: {val}".format(attr=attribute, val=value))

    def test_if_db_sync_option_works_alone(self):
        """
        Test if db --sync option is accepted without arguments.
        """
        attr = ArgOptions.SYNC
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(test_args_list=[designator, '--{0}'.format(attr)])
        value = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        assert_equals(getattr(cli.args, attr), True)

    def test_if_db_detail_option_is_stored(self):
        """
        Test if db --detail is stored correctly.
        """
        attr = ArgOptions.DETAILS
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(test_args_list=[designator, '--{0}'.format(attr)])
        value = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        assert_equals(getattr(cli.args, attr), True)

    def test_if_db_record_record_and_details_options_are_stored(self):
        """
        Test if db --records --details is accepted.
        """
        attributes = [ArgOptions.RECORDS, ArgOptions.DETAILS]
        designator = ArgSubmodules.DATABASE

        args = [designator]
        args.extend(['--{0}'.format(attr) for attr in attributes])
        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
            assert_equals(getattr(cli.args, attr), True)

    def test_if_db_records_with_details_and_filespec_options_is_stored(self):
        """
        Test if db --records --filespec_<filespec> --details is stored.
        """
        filespec_opt = 'filespec'
        filespec = "'./*.png'"
        attributes = ['records', 'details', filespec_opt]
        designator = ArgSubmodules.DATABASE
        args = [designator]
        args.extend(['--{filespec_opt}'.format(filespec_opt=filespec_opt),
                     '{filespec}'.format(filespec=filespec)])
        args.extend(['--{0}'.format(attr) for attr in attributes if
                     attr != filespec_opt])

        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, 'command'), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
            if attr == filespec_opt:
                assert_equals(getattr(cli.args, attr), filespec)
            else:
                assert_equals(getattr(cli.args, attr), True)

    @raises(SystemExit)
    def test_if_db_record_details_and_filespec_opts_wo_filespecs_errors(self):
        """
        Test if db --records --details --filespec raises an error if the
        filespec does not have a specifier (e.g. *.jpg)

        """
        file_spec = "'./*.png'"
        attributes = [ArgOptions.RECORDS, ArgOptions.DETAILS,
                      ArgOptions.FILESPEC]
        designator = ArgSubmodules.DATABASE
        args = [designator]
        args.extend(['--{0}'.format(attr) for attr in attributes])

        cli = CLIArgs(test_args_list=args)

        assert_equals(getattr(cli.args, ArgOptions.COMMAND), designator)
        for attr in attributes:
            value = getattr(cli.args, attr)
            print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
            expected = True
            if attr == ArgOptions.FILESPEC:
                expected = file_spec
            assert_equals(getattr(cli.args, attr), expected)

    @raises(SystemExit)
    def test_if_image_without_info_designator_wo_filespec_raises_error(self):
        """
        Test if image suboption without image filespec raises an error
        """
        # Proper arg list: <designator> <option> <value>
        # Actual arg list: <option> <value>

        attr = ArgOptions.IMAGE
        cli = CLIArgs(test_args_list=['--{0}'.format(attr), 'foo.tmp'])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_if_invalid_designator_raises_error(self):
        """
        Verify an invalid (unrecognized) designator raises an error.
        """
        # Proper arg list: <known_designator>
        # Actual arg list: <unknown_designator>

        designator = 'FOO'
        CLIArgs(test_args_list=[designator])
