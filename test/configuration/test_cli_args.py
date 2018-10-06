from PDL.configuration.cli_args import CLIArgs, ArgSubmodules

from nose.tools import raises


class TestCommandLine(object):

    def test_debug_flag(self):
        attr = 'debug'
        cli = CLIArgs(test_args_list=['--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        assert (attribute is True)

    def test_no_debug_flag(self):
        attr = 'debug'
        cli = CLIArgs(test_args_list=[])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))
        assert (attribute is False)

    @raises(SystemExit)
    def test_cfg_no_file(self):
        attr = 'cfg'
        cli = CLIArgs(test_args_list=['--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_inventory_detail_without_filespec(self):
        attr = 'detailed'
        cli = CLIArgs(test_args_list=[ArgSubmodules.INVENTORY, '--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_image_without_filespec(self):
        attr = 'image'
        cli = CLIArgs(test_args_list=[ArgSubmodules.INFO, '--{0}'.format(attr)])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_image_without_info_designator(self):
        attr = 'image'
        cli = CLIArgs(test_args_list=['--{0}'.format(attr), 'foo.tmp'])
        attribute = getattr(cli.args, attr)
        print("{attr} ATTRIBUTE: {val}".format(attr=attr, val=attribute))

    @raises(SystemExit)
    def test_invalid_designator(self):
        designator = 'FOO'
        CLIArgs(test_args_list=[designator])
