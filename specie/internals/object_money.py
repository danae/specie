from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjFloat
from .object_string import ObjString
from .object_record import ObjRecord


# Class that defines a money object
class ObjMoney(ObjRecord):
  # Constructor
  def __init__(self, **kwargs):
    ObjRecord.__init__(self)

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)

    self['amount'] = ObjFloat()
    self['currency'] = ObjString('EUR')

    for name, value in kwargs.items():
      self[name] = value


  ### Definition of object functions ###

  # Return the truthyness of this object
  def truthy(self):
    return ObjBool(self['amount'] != 0)

  # Return if this money object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjMoney) and (self['currency'], self['amount']) == (other['currency'], other['amount']))

  # Compare this money object with another object
  def __lt__(self, other):
    if isinstance(other, MoneyObject):
      return ObjBool(self['amount'] < other['amount'])
    raise InvalidTypeException(other)
  def __le__(self, other):
    if isinstance(other, MoneyObject):
      return ObjBool(self['amount'] <= other['amount'])
    raise InvalidTypeException(other)
  def __gt__(self, other):
    if isinstance(other, MoneyObject):
      return ObjBool(self['amount'] > other['amount'])
    raise InvalidTypeException(other)
  def __ge__(self, other):
    if isinstance(other, MoneyObject):
      return ObjBool(self['amount'] >= other['amount'])
    raise InvalidTypeException(other)


  ### Definition of conversion functions ###

  # Convert to hash
  def __hash__(self):
    return hash((self['currency'], self['amount']))

  # Convert to string
  def __str__(self):
    return f"{self['currency']} {self['amount']:.2f}"
