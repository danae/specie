from datetime import datetime, date, timedelta

from .object import Obj, ObjBool, ObjInt, ObjString
from .errors import InvalidTypeException


###########################################
### Definition of the date object class ###
###########################################

class ObjDate(Obj, typename = 'Date'):
  # The date format to use when parsing a string date
  format = "%Y-%m-%d"

  # Constructor
  def __init__(self, value = date.today()):
    super().__init__()

    if isinstance(value, ObjDate):
      self.value = value.value
    elif isinstance(value, date):
      self.value = value
    elif isinstance(value, datetime):
      self.value = value.date()
    elif isinstance(value, str):
      self.value = datetime.strptime(value, self.format).date()
    else:
      raise TypeError(f"Unexpected native type {type(value)}")


  # Return if this date object is equal to another date object
  def __eq__(self, other):
    return isinstance(other, ObjDate) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the string representation of this object
  def __str__(self):
    return self.value.strftime(self.format)

  def method_as_string(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this date object with another object
  def __lt__(self, other):
    if isinstance(other, ObjDate):
      return self.value < other.value
    return NotImplemented

  def method_lt(self, other: 'ObjDate') -> 'ObjBool':
    if (result := self.__lt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __le__(self, other):
    if isinstance(other, ObjDate):
      return self.value <= other.value
    return NotImplemented

  def method_lte(self, other: 'ObjDate') -> 'ObjBool':
    if (result := self.__le__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __gt__(self, other):
    if isinstance(other, ObjDate):
      return self.value > other.value
    return NotImplemented

  def method_gt(self, other: 'ObjDate') -> 'ObjBool':
    if (result := self.__gt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __ge__(self, other):
    if isinstance(other, ObjDate):
      return self.value >= other.value
    return NotImplemented

  def method_gte(self, other: 'ObjDate') -> 'ObjBool':
    if (result := self.__ge__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  # Return this date with a specified amount of days added
  def __add__(self, other):
    if isinstance(other, ObjInt):
      return ObjDate(self.value + timedelta(days = other.value))
    return NotImplemented

  def method_add(self, other: 'ObjInt') -> 'ObjDate':
    if (result := self.__add__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)

  # Return this date with a specified amount of days subtracted
  def __sub__(self, other):
    if isinstance(other, ObjInt):
      return ObjDate(self.value - timedelta(days = other.value))
    elif isinstance(other, ObjDate):
      return ObjInt(self.value - other.value.days)
    return NotImplemented

  def method_sub(self, other: 'ObjInt, ObjDate') -> 'ObjDate, ObjInt':
    if (result := self.__sub__(other)) != NotImplemented:
      return result
    raise InvalidTypeException(other)


  # Return the Python value of this object
  def _py_value(self):
    return self.value

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"

  # Return a formatted Python representation of this object
  def __format__(self, spec):
    return format(self.value, spec)
