import datetime
import functools

from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjInt
from .errors import InvalidTypeException


# Class that defines a date object
@functools.total_ordering
class ObjDate(Obj):
  DATE_FORMAT = "%Y-%m-%d"

  # Constructor
  def __init__(self, value = None):
    Obj.__init__(self)

    if isinstance(value, datetime.date):
      self.value = value
    elif isinstance(value, datetime.datetime):
      self.value = value.date()
    elif isinstance(value, str):
      self.value = datetime.datetime.strptime(value, self.DATE_FORMAT).date()
    elif value is None:
      self.value = datetime.date.today()
    else:
      raise TypeError(type(value))

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)
    self.set_method('add', self.__add__)
    self.set_method('sub', self.__sub__)

  # Return if this date object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjDate) and self.value == other.value)

  # Return if this date object is less than another object
  def __lt__(self, other):
    if isinstance(other, ObjDate):
      return ObjBool(self.value < other.value)
    else:
      raise InvalidTypeException(other)

  # Return this date with a specified amount of days added
  def __add__(self, other):
    if isinstance(other, ObjInt):
      return ObjDate(self.value + datetime.timedelta(days = other.value))
    else:
      raise InvalidTypeException(other)

  # Return this date with a specified amount of days subtracted
  def __sub__(self, other):
    if isinstance(other, ObjInt):
      return DateObject(self.value - datetime.timedelta(days = other.value))
    elif isinstance(other, ObjDate):
      return ObjInt((self.value - other.value).days)
    else:
      raise InvalidTypeException(other)

  # Convert to hash
  def __hash__(self):
    return hash((self.value))

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"

  # Convert to string
  def __str__(self):
    return self.value.strftime(self.DATE_FORMAT)
