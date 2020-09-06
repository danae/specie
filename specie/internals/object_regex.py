import re

from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException


# Class that defines a regex object
class ObjRegex(Obj):
  # Constructor
  def __init__(self, regex_value):
    Obj.__init__(self)

    if isinstance(regex_value, str):
      self.regex_value = re.compile(regex_value, re.IGNORECASE)
    else:
      raise TypeError(type(regex_value))


  ### Definition of object functions ###

  # Return the primitive value of this object
  def value(self):
    return self.regex_value

  # Return if this regex object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjRegex) and self.value() == other.value())


  ### Definition of conversion functions

  # Convert to string
  def __str__(self):
    return f"regex \"{self.value().pattern}\""

  # Convert to representation
  def __repr__(self):
    return "{}({!r})".format(self.__class__.__name__, self.value())
