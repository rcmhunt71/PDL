import importlib
import inspect
from typing import Callable

from PDL.logger.logger import Logger

log = Logger()


class ClassNotFoundInImportedModule(Exception):
    def __init__(self, module: str, klass: str) -> None:
        self.message = f"Class '{klass}' not found in module {module}"


"""
This module provides the basic functionality to take a given dotted path (str) to a module or class,
and import the module/class. This allows a user to specify which classes to import for use
within the application. 

Application Use Case:
For a given use, the modules have the same base class, so there are well defined/identified
interfaces, and the imported class is assigned to a generic variable that can used.

   Example:
   ========
       target_class_a = project.foo.module.ClassA
       target_class_b = project.foo.module.ClassB

       for klass in [target_class_a, target_class_b]:
          MyClassDef = import_module_class(klass)
          my_class = MyClassDef(<params>)
          my_class.method1()
          print my_class.method2()  

 
Both classes have been dynamically loaded, instantiated, and methods invoked by generalization.
As long as each imported class contains at least the same invoked methods (built-in assumption), 
any class can be called/utilized.
 
"""


def import_module(dotted_path_module: str) -> Callable:
    """
    Imports a module into memory.
    :param dotted_path_module: from.here.you.can.find.the.module
    :return: Reference to the imported module

    """
    log.debug(f"Attempting to import module '{dotted_path_module}' into memory.")
    module = None
    try:
        module = importlib.import_module(name=dotted_path_module)
        log.debug(f"SUCCESS: Import of '{dotted_path_module}'")
    except ImportError as exc:
        msg = f"Unable to import: '{dotted_path_module}' --> {exc}"
        log.error(msg)
        log.error(build_stack_trace(inspect.stack()))

    return module


def import_module_class(dotted_path_class: str) -> Callable:
    """
    Imports the class from the module. Given a module reference, get the class.

    :param dotted_path_class: this.is.a.module.Class
    :return: Reference to the class

    """
    log.debug(f"Attempting to import class '{dotted_path_class}' into memory.")

    parts = dotted_path_class.split('.')
    klass = parts[-1]
    path = '.'.join(parts[:-1])

    module = import_module(dotted_path_module=path)

    if klass not in dir(module):
        log.error(f"Class ({klass}) not found in module: {path}")
        msg = ("Available classes, routines, and variables available in "
               "{module}:\n{avail}")
        log.debug(msg.format(module=path, avail=', '.join(
            [x for x in dir(module) if not x.startswith('_')])))

        raise ClassNotFoundInImportedModule(klass=klass, module=path)

    log.debug(f"Returning requested imported class '{klass}'.")
    return getattr(module, klass, None)


def build_stack_trace(trace: list):
    stack_fmt = "\n{path}:L{lineno}\n\tROUTINE: {routine}\n\tCODE: {code}\n"
    stack_trace = ''
    for stack in trace:
        stack_trace += stack_fmt.format(
            path=stack[1], lineno=stack[2], routine=stack[3], code=stack[4][0].strip())
    return stack_trace
