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

    self.set_field('amount', ObjFloat())
    self.set_field('currency', ObjString('EUR'))

    for name, value in kwargs.items():
      self.set_field(name, value)

  # Return the truthyness of this object
  def truthy(self):
    return ObjBool(self.get_field('amount') != 0)

  # Return if this money object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjMoney) and (self.get_field('currency'), self.get_field('amount')) == (other.get_field('currency'), other.get_field('amount')))

  # Return if this money object is less than another transaction
  def __lt__(self, other):
    if isinstance(other, MoneyObject):
      return ObjBool(self.get_field('amount') < other.get_field('amount'))
    else:
      raise InvalidTypeException(other)

  # Convert to hash
  def __hash__(self):
    return hash((self.get_field('currency'), self.get_field('amount')))
