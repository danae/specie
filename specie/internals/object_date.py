import functools

from datetime import datetime, date, timedelta

from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjInt
from .errors import InvalidTypeException


# Class that defines a date object
@functools.total_ordering
class ObjDate(Obj):
  DATE_FORMAT = "%Y-%m-%d"

  # Constructor
  def __init__(self, date_value = date.today()):
    Obj.__init__(self)

    if isinstance(date_value, date):
      self.date_value = date_value
    elif isinstance(date_value, datetime):
      self.date_value = date_value.date()
    elif isinstance(date_value, str):
      self.date_value = datetime.strptime(date_value, self.DATE_FORMAT).date()
    else:
      raise TypeError(type(date_value))

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)
    self.set_method('add', self.__add__)
    self.set_method('sub', self.__sub__)

  # Return the primitive value of this object
  def value(self):
    return self.date_value

  # Return if this date object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjDate) and self.value() == other.value())

  # Return if this date object is less than another object
  def __lt__(self, other):
    if isinstance(other, ObjDate):
      return ObjBool(self.value() < other.value())
    raise InvalidTypeException(other)

  # Return this date with a specified amount of days added
  def __add__(self, other):
    if isinstance(other, ObjInt):
      return ObjDate(self.value() + datetime.timedelta(days = other.value()))
    raise InvalidTypeException(other)

  # Return this date with a specified amount of days subtracted
  def __sub__(self, other):
    if isinstance(other, ObjInt):
      return DateObject(self.value() - datetime.timedelta(days = other.value()))
    elif isinstance(other, ObjDate):
      return ObjInt((self.value() - other.value()).days)
    raise InvalidTypeException(other)

  # Convert to hash
  def __hash__(self):
    return hash((self.value()))

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value()!r})"

  # Convert to string
  def __str__(self):
    return self.value().strftime(self.DATE_FORMAT)
