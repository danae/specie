from .object import Obj, ObjBool, ObjInt, ObjString
from .object_record import ObjRecord


#####################################
### Definition of the money class ###
#####################################

class ObjMoney(ObjRecord, typename = "Money"):
  # Constructor
  def __init__(self, currency, amount):
    super().__init__(currency = currency, amount = amount)


  # Return if this money object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjMoney) and (self['currency'], self['amount']) == (other['currency'], other['amount'])

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return self['amount'] != 0

  def method_asBool(self):
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return f"{self['currency']} {self['amount']:.2f}"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash((self['currency'], self['amount']))

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this money object with another object
  def __lt__(self, other):
    if isinstance(other, ObjMoney):
      return (self['date'], self['id']) < (other['date'], other['id'])
    return NotImplemented

  def method_lt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__lt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __le__(self, other):
    if isinstance(other, ObjMoney):
      return self['amount'] < other['amount']
    return NotImplemented

  def method_lte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__le__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __gt__(self, other):
    if isinstance(other, ObjMoney):
      return self['amount'] > other['amount']
    return NotImplemented

  def method_gt(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__gt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __ge__(self, other):
    if isinstance(other, ObjMoney):
      return self['amount'] >= other['amount']
    return NotImplemented

  def method_gte(self, other: 'ObjMoney') -> 'ObjBool':
    if (result := self.__ge__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)
