import importlib
import inspect

from PDL.logger.logger import Logger

log = Logger()


class ClassNotFoundInImportedModule(Exception):
    def __init__(self, module: str, klass: str) -> None:
        self.message = f"Class '{klass}' not found in module {module}"


# TODO: Add docstrings
# TODO: Look up and add return type of unknown module

def import_module(dotted_path_module: str):
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


# TODO: Look up and add return type of unknown class

def import_module_class(dotted_path_class: str):
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


# TODO: Look up and add return type for trace

def build_stack_trace(trace):
    stack_fmt = "\n{path}:L{lineno}\n\tROUTINE: {routine}\n\tCODE: {code}\n"
    stack_trace = ''
    for stack in trace:
        stack_trace += stack_fmt.format(path=stack[1], lineno=stack[2],
                                        routine=stack[3], code=stack[4][0].strip())
    return stack_trace
