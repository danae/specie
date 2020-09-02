import functools
import re

from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException


# Class that defines a string object
@functools.total_ordering
class ObjString(Obj):
  # Constructor
  def __init__(self, value = None):
    Obj.__init__(self)

    if isinstance(value, str):
      self.value = value
    elif value is None:
      self.value = ""
    else:
      raise TypeError(type(value))

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)
    self.set_method('add', self.__add__)
    self.set_method('contains', self.contains)
    self.set_method('match', self.match)

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(bool(self.value))

  # Return if this string object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjString) and self.value == other.value)

  # Return if this string object is less than another object
  def __lt__(self, other):
    if isinstance(other, ObjString):
      return ObjBool(self.value < other.value)
    else:
      raise InvalidTypeException(other)

  # Return the concatenation of two string objects
  def __add__(self, other):
    if isinstance(other, ObjString):
      return ObjString(self.value + other.value)
    else:
      raise InvalidTypeException(pattern)

  # Return if this string object contains another string object
  def contains(self, sub):
    if isinstance(sub, ObjString):
      return ObjBool(self.value.find(sub.value) > -1)
    else:
      raise InvalidTypeException(sub)

  # Return if this string object matches a pattern
  def match(self, pattern):
    if isinstance(pattern, ObjString):
      return ObjBool(re.search(pattern.value, self.value, re.IGNORECASE) is not None)
    else:
      raise InvalidTypeException(pattern)

  # Convert to string
  def __str__(self):
    return self.value

  # Convert to representation
  def __repr__(self):
    return "{}({!r})".format(self.__class__.__name__, self.value)
