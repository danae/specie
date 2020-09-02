import functools

from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException


# Class that defines a numeric object
@functools.total_ordering
class ObjNumeric(Obj):
  # Constructor
  def __init__(self, value):
    Obj.__init__(self)

    self.value = value

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)
    self.set_method('add', self.__add__)
    self.set_method('sub', self.__sub__)
    self.set_method('mul', self.__mul__)
    self.set_method('div', self.__truediv__)

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(bool(self.value))

  # Return if this numeric object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjNumeric) and self.value == other.value)

  # Return if this numeric is less than another object
  def __lt__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjBool(self.value < other.value)
    else:
      raise InvalidTypeException(other)

  # Return the addition of two numeric objects
  def __add__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjNumeric(self.value + other.value)
    else:
      raise InvalidTypeException(other)

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjNumeric(self.value - other.value)
    else:
      raise InvalidTypeException(other)

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjNumeric(self.value * other.value)
    else:
      raise InvalidTypeException(other)

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjNumeric(self.value / other.value)
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
    return str(self.value)


# Class that defines an integer object
class ObjInt(ObjNumeric):
  # Constructor
  def __init__(self, value = None):
    if isinstance(value, int):
      ObjNumeric.__init__(self, value)
    elif isinstance(value, str):
      ObjNumeric.__init__(self, int(value))
    elif value is None:
      ObjNumeric.__init__(self, 0)
    else:
      raise TypeError(type(value))

  # Convert to int
  def __int__(self):
    return self.value


# Class that defines a float object
class ObjFloat(ObjNumeric):
  def __init__(self, value = None):
    if isinstance(value, float):
      ObjNumeric.__init__(self, value)
    elif isinstance(value, str):
      ObjNumeric.__init__(self, float(value))
    elif value is None:
      ObjNumeric.__init__(self, 0)
    else:
      raise TypeError(type(value))

  # Convert to float
  def __float__(self):
    return self.value
