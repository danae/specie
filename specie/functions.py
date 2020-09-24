import traceback

from . import internals, output


# Class that defines the print function
class PrintFunction(internals.ObjCallable, typename = "Native_print"):
  # Constructor
  def __init__(self):
    super().__init__()

  # Return the required arguments of the function
  def required_args(self):
    return [internals.Obj]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, *args, **kwargs):
    output.print_object(*args, **kwargs)


# Class that defines the print_title function
class PrintTitleFunction(internals.ObjCallable, typename = 'Native_print_title'):
  # Constructor
  def __init__(self):
    super().__init__()

  # Return the required arguments of the function
  def required_args(self):
    return [internals.ObjString]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, *args, **kwargs):
    output.title(*args, **kwargs)


# Class that defines the include function
class IncludeFunction(internals.ObjCallable, typename = 'Native_include'):
  # Constructor
  def __init__(self):
    super().__init__()

  # Return the required arguments of the function
  def required_args(self):
    return [internals.ObjString]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, *args, **kwargs):
    args = [arg._py_value() if isinstance(arg, internals.Obj) else arg for arg in args]
    kwargs = {name: kwarg._py_value() if isinstance(kwarg, internals.Obj) else kwarg for name, kwarg in kwargs.items()}
    return interpreter.execute_include(*args, **kwargs)


# Class that defines the import function
class ImportFunction(internals.ObjCallable, typename = 'Native_import'):
  # Constructor
  def __init__(self):
    super().__init__()

  # Return the required arguments of the function
  def required_args(self):
    return [internals.ObjString]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {'type': internals.ObjString}

  # Call the function
  def call(self, interpreter, *args, **kwargs):
    args = [arg._py_value() if isinstance(arg, internals.Obj) else arg for arg in args]
    kwargs = {name: kwarg._py_value() if isinstance(kwarg, internals.Obj) else kwarg for name, kwarg in kwargs.items()}
    return interpreter.execute_import(*args, **kwargs)
