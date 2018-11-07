import importlib
import inspect

from PDL.logger.logger import Logger

log = Logger()


def import_module(dotted_path_module):
    """
    Imports a module into memory.
    :param dotted_path_module: from.here.you.can.find.the.module
    :return: Reference to the imported module

    """
    log.debug("Attempting to import module '{0}' into memory.".format(dotted_path_module))
    module = None
    try:
        module = importlib.import_module(name=dotted_path_module)
        log.debug("Import of '{0}' was successful.".format(dotted_path_module))
    except ImportError as exc:
        msg = "Unable to import: '{module}' --> {exc}".format(module=dotted_path_module, exc=exc.message)
        log.error(msg)
        log.error(build_stack_trace(inspect.stack()))

    return module


def import_module_class(dotted_path_class):
    """
    Imports the class from the module. Given a module reference, get the class.

    :param dotted_path_class: this.is.a.module.Class
    :return: Reference to the class

    """
    log.debug("Attempting to import class '{0}' into memory.".format(dotted_path_class))

    parts = dotted_path_class.split('.')
    klass = parts[-1]
    path = '.'.join(parts[:-1])

    module = import_module(dotted_path_module=path)
    return getattr(module, klass, None)


def build_stack_trace(trace):
    stack_fmt = "\n{path}:L{lineno}\n\tROUTINE: {routine}\n\tCODE: {code}\n"
    stack_trace = ''
    for stack in trace:
        stack_trace += stack_fmt.format(path=stack[1], lineno=stack[2],
                                        routine=stack[3], code=stack[4][0].strip())
    return stack_trace
