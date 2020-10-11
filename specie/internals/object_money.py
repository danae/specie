from .object import Obj, ObjBool, ObjNumber, ObjInt, ObjFloat, ObjString
from .object_record import ObjRecord


############################################
### Definition of the money object class ###
############################################

class ObjMoney(ObjRecord, typename = "Money"):
  # Constructor
  def __init__(self, currency: 'ObjString', value: 'ObjNumber') -> 'ObjMoney':
    super().__init__(currency = currency, value = ObjFloat(value))


  # Return if this money object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjMoney) and (self['currency'], self['value']) == (other['currency'], other['value'])

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return self['value'] != 0

  def method_asBool(self):
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return f"{self['currency']} {self['value']:.2f}"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash((self['currency'], self['value']))

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this money object with another object
  def __lt__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return self['value'] < other['value']
    return NotImplemented

  def method_lt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__lt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __le__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return self['value'] <= other['value']
    return NotImplemented

  def method_lte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__le__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __gt__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return self['value'] > other['value']
    return NotImplemented

  def method_gt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__gt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __ge__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return self['value'] >= other['value']
    return NotImplemented

  def method_gte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__ge__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def method_cmp(self, other: 'ObjMoney') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
    raise InvalidTypeException(other)

  # Return the addition of two money objects
  def __add__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return ObjMoney(self['currency'], self['value'] + other['value'])
    return NotImplemented

  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__add__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjMoney) and self['currency'] == other['currency']:
      return ObjMoney(self['currency'], self['value'] - other['value'])
    return NotImplemented

  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__sub__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjNumber):
      return ObjMoney(self['currency'], self['value'] * other)
    return NotImplemented

  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__mul__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumber):
      return ObjMoney(self['currency'], self['value'] / other)
    return NotImplemented

  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__truediv__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)
