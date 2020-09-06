import traceback

from . import internals, output


# Class that defines the print function
class PrintFunction(internals.Callable):
  # Return the signature of this function
  def signature(self):
    return internals.CallableSignature([internals.Obj])

  # Call the function
  def call(self, interpreter, arguments, keywords):
    output.print_object(*arguments, **keywords.value())


# Class that defines the print_title function
class PrintTitleFunction(internals.Callable):
  # Return the signature of this function
  def signature(self):
    return internals.CallableSignature([internals.Obj])

  # Call the function
  def call(self, interpreter, arguments, keywords):
    output.title(*arguments.value(), **keywords.value())


# Class that defines the include function
class IncludeFunction(internals.Callable):
  # Return the signature of this function
  def signature(self):
    return internals.CallableSignature([internals.ObjString])

  # Call the function
  def call(self, interpreter, arguments, keywords):
    return interpreter.execute_include(*arguments.value(), **keywords.value())


# Class that defines the import function
class ImportFunction(internals.Callable):
  # Return the signature of this function
  def signature(self):
    return internals.CallableSignature([internals.ObjString], {'type': internals.ObjString})

  # Call the function
  def call(self, interpreter, arguments, keywords):
    return interpreter.execute_import(*arguments.value(), **keywords.value())
