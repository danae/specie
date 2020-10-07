from .object import Obj, ObjBool, ObjInt, ObjString
from .object_callable import ObjCallable
from .object_record import ObjRecord
from .errors import RuntimeException


########################################
### Definition of the importer class ###
########################################

class ObjImporter(ObjCallable):
  # Constructor
  def __init__(self, interpreter):
    super().__init__()
    self.interpreter = interpreter

  # Return the parameters of the callable
  def parameters(self):
    return [ObjString, ObjRecord]

  # Call the importer
  def __call__(self, file_name, options):
    file_name = file_name._py_value() if isinstance(file_name, ObjString) else file_name
    options = options._py_dict() if isinstance(options, ObjRecord) else options

    # Check if the file exists
    if (resolved_file_name := self.interpreter.resolve_file_name(file_name)) is None:
      raise RuntimeException(f"Import failed: the file '{file_name}' could not be found")

    # Import the transactions
    transactions = self.do(resolved_file_name, options)

    # Add the imported transactions
    self.interpreter.globals['_'].insert_all(transactions)

    # Return a result object
    return ObjRecord(count = ObjInt(len(transactions)))

  # Import a file with transactions
  def do(self, file_name, options):
    raise NotImplementedError()
