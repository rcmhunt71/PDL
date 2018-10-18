from PDL.configuration.cli.args import CLIArgs, ArgSubmodules

from nose.tools import raises, assert_equals, assert_false, assert_true


class TestCommandLine(object):

    def test_debug_flag(self):
        attr = 'debug'
        cli_args = ['--{0}'.format(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._resp_should_be_bool(attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_no_debug_flag(self):
        attr = 'debug'
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._resp_should_be_bool(attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_dryrun_flag(self):
        attr = 'dryrun'
        cli_args = ['--{0}'.format(attr), ArgSubmodules.DOWNLOAD]
        expectation = True
        self._resp_should_be_bool(attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def test_no_dryrun_flag(self):
        attr = 'dryrun'
        cli_args = [ArgSubmodules.DOWNLOAD]
        expectation = False
        self._resp_should_be_bool(attr=attr, cli_args=cli_args, bool_expectation=expectation)

    def _resp_should_be_bool(self, attr, cli_args, bool_expectation):
        cli = CLIArgs(test_args_list=cli_args)
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        if bool_expectation:
            assert_true(attribute)
        else:
            assert_false(attribute)

    def test_command_attr_set(self):
        attr = 'command'
        designator = ArgSubmodules.DOWNLOAD

        cli = CLIArgs(test_args_list=[designator, "www.foo.com/this/is/my/utl.html"])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        assert_equals(attribute, designator)

# --------- Improper CLI Argument Sets -------------

    @raises(SystemExit)
    def test_cfg_no_file(self):
        # Proper arg list: --cfg <filespec>
        # Actual arg list: --cfg

        attr = 'cfg'
        cli = CLIArgs(test_args_list=['--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_image_without_filespec(self):
        # Proper arg list: info image <filespec>
        # Actual arg list: info image

        attr = 'image'
        cli = CLIArgs(test_args_list=[ArgSubmodules.INFO, '--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_db_sync_and_records_mutually_exclusive(self):
        attr = ['sync', 'records']
        cli = CLIArgs(test_args_list=['--{0}'.format(attr[0]), '--{0}'.format(attr[1])])
        for attribute in attr:
            value = getattr(cli.args, attribute)
            print("{attr} ATTRIBUTE: {val}".format(attr=attribute, val=value))

    def test_db_sync_alone(self):
        attr = 'sync'
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(test_args_list=[designator, '--{0}'.format(attr)])
        value = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
        assert_equals(getattr(cli.args, 'command'), designator)
        assert_equals(getattr(cli.args, attr), True)

    def test_db_record_options(self):
        attr = 'details'
        designator = ArgSubmodules.DATABASE
        cli = CLIArgs(test_args_list=[designator, '--{0}'.format(attr)])
        value = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=value))
        assert_equals(getattr(cli.args, 'command'), designator)
        assert_equals(getattr(cli.args, attr), True)


    @raises(SystemExit)
    def test_image_without_info_designator(self):
        # Proper arg list: <designator> <option> <value>
        # Actual arg list: <option> <value>

        attr = 'image'
        cli = CLIArgs(test_args_list=['--{0}'.format(attr), 'foo.tmp'])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_invalid_designator(self):
        # Proper arg list: <known_designator>
        # Actual arg list: <unknown_designator>
        designator = 'FOO'
        CLIArgs(test_args_list=[designator])


