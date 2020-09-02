import functools

from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjFloat
from .object_string import ObjString
from .object_date import ObjDate
from .object_record import ObjRecord
from .object_money import ObjMoney
from .errors import InvalidTypeException


# Class that defines a transaction object
@functools.total_ordering
class ObjTransaction(ObjRecord):
  # Constructor
  def __init__(self, **kwargs):
    ObjRecord.__init__(self)

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)

    self.set_field('id', ObjString())
    self.set_field('date', ObjDate())
    self.set_field('amount', ObjMoney(currency = ObjString('EUR'), amount = ObjFloat()))
    self.set_field('label', ObjString())
    self.set_field('name', ObjString())
    self.set_field('address', ObjString())
    self.set_field('description', ObjString())

    for name, value in kwargs.items():
      self.set_field(name, value)

  # Return if this transaction object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjTransaction) and self.get_field('id') == other.get_field('id'))

  # Return if this transaction object is less than another transaction
  def __lt__(self, other):
    if isinstance(other, ObjTransaction):
      return ObjBool((self.get_field('date'), self.get_field('id')) < (other.get_field('date'), other.get_field('id')))
    else:
      raise InvalidTypeException(other)

  # Convert to hash
  def __hash__(self):
    return hash((self.get_field('id')))
