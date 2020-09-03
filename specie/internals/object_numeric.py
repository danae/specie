import functools

from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException


# Class that defines a numeric object
@functools.total_ordering
class ObjNumeric(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)

    self.set_method('lt', self.__lt__)
    self.set_method('lte', self.__le__)
    self.set_method('gt', self.__gt__)
    self.set_method('gte', self.__ge__)
    self.set_method('add', self.__add__)
    self.set_method('sub', self.__sub__)
    self.set_method('mul', self.__mul__)
    self.set_method('div', self.__truediv__)

  # Return the primitive value of this object
  def value(self):
    raise NotImplementedError(f"This function must be implemented by subclasses of {self.__class__.__name__}")

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(bool(self.value()))

  # Return if this numeric object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjNumeric) and self.value() == other.value())

  # Return if this numeric is less than another object
  def __lt__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjBool(self.value() < other.value())
    raise InvalidTypeException(other)

  # Return the addition of two numeric objects
  def __add__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjFloat(self.value() + other.value())
    raise InvalidTypeException(other)

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjFloat(self.value() - other.value())
    raise InvalidTypeException(other)

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjFloat(self.value() * other.value())
    raise InvalidTypeException(other)

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumeric):
      return ObjFloat(self.value() / other.value())
    raise InvalidTypeException(other)

  # Convert to hash
  def __hash__(self):
    return hash((self.value()))

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value()!r})"

  # Convert to string
  def __str__(self):
    return str(self.value())

  # Convert to int
  def __int__(self):
    return int(self.value())

  # Convert to float
  def __float__(self):
    return float(self.value())


# Class that defines an integer object
class ObjInt(ObjNumeric):
  # Constructor
  def __init__(self, int_value = 0):
    ObjNumeric.__init__(self)

    if isinstance(int_value, int):
      self.int_value = int_value
    elif isinstance(int_value, str):
      self.int_value = int(int_value)
    else:
      raise TypeError(type(int_value))

  # Return the primitive value of this object
  def value(self):
    return self.int_value


# Class that defines a float object
class ObjFloat(ObjNumeric):
  def __init__(self, float_value = 0.0):
    ObjNumeric.__init__(self)

    if isinstance(float_value, float):
      self.float_value = float_value
    elif isinstance(float_value, str):
      self.float_value = float(float_value)
    else:
      raise TypeError(type(float_value))

  # Return the primitive value of this object
  def value(self):
    return self.float_value
