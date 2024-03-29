from .object import Obj, ObjBool, ObjNumber, ObjInt, ObjFloat, ObjString
from .object_record import ObjRecord
from .errors import InvalidOperationException


############################################
### Definition of the money object class ###
############################################

class ObjMoney(ObjRecord, typename = "Money", prettyprint = False):
  # Constructor
  def __init__(self, currency: 'ObjString', value: 'ObjNumber' = 0.0) -> 'ObjMoney':
    super().__init__()
    self.declare_field('currency', ObjString(currency))
    self.declare_field('value', ObjFloat(value))


  # Return if this money object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjMoney) and (self['currency'], self['value']) == (other['currency'], other['value'])

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return self.value != ObjFloat(0.0)

  def method_asBool(self):
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    if float(self.value) < 0.0:
      return f"[red]{self.currency} {self.value:.2f}"
    else:
      return f"{self.currency} {self.value:.2f}"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash((self.currency, self.value))

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this money object with another object
  def __lt__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return self.value < other.value
    return NotImplemented

  def method_lt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__lt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __le__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return self.value <= other.value
    return NotImplemented

  def method_lte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__le__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lte' does not support operands of type {self.__class__} and {other.__class__}")

  def __gt__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return self.value > other.value
    return NotImplemented

  def method_gt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__gt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'gt' does not support operands of type {self.__class__} and {other.__class__}")

  def __ge__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return self.value >= other.value
    return NotImplemented

  def method_gte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__ge__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'gte' does not support operands of type {self.__class__} and {other.__class__}")

  def method_cmp(self, other: 'ObjMoney') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
    raise InvalidOperationException(f"Operation 'cmp' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the addition of two money objects
  def __add__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return ObjMoney(self.currency, self.value + other.value)
    return NotImplemented

  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__add__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'add' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjMoney) and self.currency == other.currency:
      return ObjMoney(self.currency, self.value - other.value)
    return NotImplemented

  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__sub__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'sub' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjNumber):
      return ObjMoney(self.currency, self.value * other)
    return NotImplemented

  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__mul__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'mul' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumber):
      return ObjMoney(self.currency, self.value / other)
    return NotImplemented

  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__truediv__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'div' does not support operands of type {self.__class__} and {other.__class__}")
