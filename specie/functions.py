import traceback

from . import internals, output


# Class that defines the print function
class PrintFunction(internals.ObjCallable):
  # Return the required arguments of the function
  def required_args(self):
    return [internals.Obj]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, arguments, keywords):
    output.print_object(*arguments, **keywords.value())


# Class that defines the print_title function
class PrintTitleFunction(internals.ObjCallable):
  # Return the required arguments of the function
  def required_args(self):
    return [internals.Obj]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, args, kwargs):
    output.title(*args.value(), **kwargs.value())


# Class that defines the include function
class IncludeFunction(internals.ObjCallable):
  # Return the required arguments of the function
  def required_args(self):
    return [internals.ObjString]

  # Call the function
  def call(self, interpreter, args, kwargs):
    return interpreter.execute_include(*args.value(), **kwargs.value())


# Class that defines the import function
class ImportFunction(internals.ObjCallable):
  # Return the required arguments of the function
  def required_args(self):
    return [internals.ObjString]

  # Return the required keywords of the function
  def required_kwargs(self):
    return {'type': ObjString}

  # Call the function
  def call(self, interpreter, args, kwargs):
    return interpreter.execute_import(*args.value(), **kwargs.value())
