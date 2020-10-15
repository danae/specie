from .object import Obj, ObjBool, ObjInt, ObjFloat, ObjString
from .object_record import FieldOptions, ObjRecord
from .object_date import ObjDate
from .object_money import ObjMoney
from .errors import InvalidOperationException


##################################################
### Definition of the transaction object class ###
##################################################

class ObjTransaction(ObjRecord, typename = "Transaction"):
  # Constructor
  def __init__(self):
    super().__init__()
    self.declare_field('id', ObjString(), public = False)
    self.declare_field('source', ObjString(), public = False)
    self.declare_field('date', ObjDate())
    self.declare_field('amount', ObjMoney(ObjString('EUR')), options = FieldOptions.FORMAT_ALIGN_RIGHT)
    self.declare_field('label', ObjString())
    self.declare_field('name', ObjString())
    self.declare_field('address', ObjString())
    self.declare_field('description', ObjString(), options = FieldOptions.FORMAT_ELLIPSIS)


  # Return if this transaction object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjTransaction) and self.id == other.id

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the hash of this object
  def __hash__(self):
    return hash((self.id))

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this transaction object with another object
  def __lt__(self, other):
    if isinstance(other, ObjTransaction):
      return (self.date, self.id) < (other.date, other.id)
    return NotImplemented

  def method_lt(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__lt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __le__(self, other):
    if isinstance(other, ObjTransaction):
      return (self.date, self.id) <= (other.date, other.id)
    return NotImplemented

  def method_lte(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__le__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lte' does not support operands of type {self.__class__} and {other.__class__}")

  def __gt__(self, other):
    if isinstance(other, ObjTransaction):
      return (self.date, self.id) > (other.date, other.id)
    return NotImplemented

  def method_gt(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__gt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'gt' does not support operands of type {self.__class__} and {other.__class__}")

  def __ge__(self, other):
    if isinstance(other, ObjTransaction):
      return (self.date, self.id) >= (other.date, other.id)
    return NotImplemented

  def method_gte(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__ge__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'gte' does not support operands of type {self.__class__} and {other.__class__}")

  def method_cmp(self, other: 'ObjTransaction') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
    raise InvalidOperationException(f"Operation 'cmp' does not support operands of type {self.__class__} and {other.__class__}")
