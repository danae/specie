# Import errors
from .errors import (RuntimeException, InvalidStateException,
  InvalidTypeException, InvalidValueException, InvalidCallException,
  UndefinedMethodException, UndefinedFieldException, UndefinedIndexException)

# Import parameters
from .parameters import (Parameter, ParameterRequired, ParameterVariadic,
  Parameters)

# Import primitive objects
from .object import (Obj, ObjNull, ObjBool, ObjNumber, ObjInt, ObjFloat,
  ObjString, ObjRegex)

# Import objects
from .object_callable import ObjCallable, ObjPartialCallable, ObjPyCallable
from .object_function import ObjFunction
from .object_iterable import ObjIterable, ObjDelegatedIterable, ObjIterator
from .object_list import ObjList, ObjListIterator
from .object_record import FieldOptions, Field, ObjRecord
from .object_date import ObjDate
from .object_money import ObjMoney
from .object_transaction import ObjTransaction
from .object_importer import ObjImporter
from .object_importer_rabobank import ObjRabobankImporter
from .object_importer_n26 import ObjN26Importer
from .object_importer_paypal import ObjPayPalImporter


# Create the import namespace
def namespace_import(interpreter):
  ns = ObjRecord()
  ns['rabobank'] = ObjRabobankImporter(interpreter)
  ns['n26'] = ObjN26Importer(interpreter)
  ns['paypal'] = ObjPayPalImporter(interpreter, ObjString("EUR"))
  return ns
