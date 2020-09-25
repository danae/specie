from ..internals import *


# Import standard library objects
from .object_money import ObjMoney
from .object_transaction import ObjTransaction


# Create std namespace
def namespace_std(interpreter):
  namespace = ObjRecord()
  namespace['Money'] = ObjNativeCallable(ObjMoney, [ObjString, ObjInt])
  namespace['Transaction'] = ObjNativeCallable(ObjTransaction, [ObjRecord])
  namespace['RabobankImporter'] = ObjNativeCallable(lambda: ObjRabobankImporter(interpreter), [])
  return namespace
