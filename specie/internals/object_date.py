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
  def __init__(self, value: 'ObjDate, ObjString' = date.today()) -> 'ObjDate':
    super().__init__()

    if isinstance(value, ObjDate):
      self.value = value.value
    elif isinstance(value, ObjString):
      try:
        self.value = datetime.strptime(value.value, self.format).date()
      except ValueError:
        raise RuntimeException(f"Invalid date literal {value}")
    elif isinstance(value, datetime):
      self.value = value.date()
    elif isinstance(value, date):
      self.value = value
    elif isinstance(value, str):
      try:
        self.value = datetime.strptime(value, self.format).date()
      except ValueError:
        raise RuntimeException(f"Invalid date literal {value}")
    else:
      raise TypeError(f"Unexpected native type {value.__class__.__name__}")


  # Return if this date object is equal to another date object
  def __eq__(self, other):
    return isinstance(other, ObjDate) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the string representation of this object
  def __str__(self):
    return self.value.strftime(self.format)

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the date components of this date object
  def year(self):
    return self.value.year

  def method_year(self) -> 'ObjInt':
    return ObjInt(self.year())

  def month(self):
    return self.value.month

  def method_month(self) -> 'ObjInt':
    return ObjInt(self.month())

  def day(self):
    return self.value.day

  def method_day(self) -> 'ObjInt':
    return ObjInt(self.day())

  def at_start_of_year(self):
    return date(self.value.year, 1, 1)

  def method_atStartOfYear(self) -> 'ObjDate':
    return ObjDate(self.at_start_of_year())

  def at_start_of_month(self):
    return date(self.value.year, self.value.month, 1)

  def method_atStartOfMonth(self) -> 'ObjDate':
    return ObjDate(self.at_start_of_month())

  # Return a formatted string representation of this date object
  def __format__(self, format_spec):
    if isinstance(format_spec, (ObjString, str)):
      format_spec = format_spec.value if isinstance(format_spec, ObjString) else format_spec
      return format(self.value, format_spec)
    raise InvalidTypeException(format_spec)

  def method_asFormat(self, format_spec: 'ObjString') -> 'ObjString':
    return ObjString(self.__format__(format_spec))

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

  def method_cmp(self, other: 'ObjDate') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
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
