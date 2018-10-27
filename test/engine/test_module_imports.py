import sys

import PDL.engine.module_imports as imports

from nose.tools import assert_equals, assert_not_equals, assert_true, assert_false


class TestModuleImports(object):

    def test_does_existing_module_loads(self):
        module_to_load = "PDL.test.engine.class_test"
        imports.import_module(module_to_load)

        for x in sorted(sys.modules.keys()):
            print(x)

        assert module_to_load in sys.modules

    def test_does_existing_class_loads(self):
        test_value = "test"
        module_to_load = "PDL.test.engine.class_test.ClassFoo"

        test_class = imports.import_module_class(module_to_load)
        test_instance = test_class(test_value)

        assert isinstance(test_instance, test_class)
        assert_equals(test_instance.name, test_value)
