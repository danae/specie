import functools
import importlib
import inspect
import re
import sys
import types

from .parameters import Parameter, ParameterRequired, ParameterVariadic, Parameters
from .errors import RuntimeException, InvalidOperationException, InvalidTypeException, UndefinedMethodException, UndefinedIndexException


######################################
### Definition of the method class ###
######################################

class Method:
  # Constructor
  def __init__(self, cls, func):
    self.cls = cls
    self.func = func

  # Resolve the method to a callable
  def create_callable(self, this_arg):
    from .object_callable import ObjPyCallable
    return ObjPyCallable(self.func, self.cls).partial(this_arg)


###########################################
### Definition of the object meta class ###
###########################################

class ObjMeta(type):
  # Dict that holds all defined classes
  obj_classes = {}

  # Class constructor
  def __new__(cls, name, bases, attrs, **kwargs):
    return super().__new__(cls, name, bases, attrs)

  # Class initializer
  def __init__(cls, name, bases, attrs, **kwargs):
    super().__init__(name, bases, attrs)

    # Add this class to the classes dict
    cls.obj_classes[name] = cls

    # Set the typename of the class
    cls.typename = kwargs.get('typename', cls.__name__)

    # Set the methods by iterating over the attributes
    cls.methods = {}

    for attr in dir(cls):
      if not attr.startswith('method_'):
        continue

      method_func = getattr(cls, attr)
      method_name = attr[7:]
      cls.methods[method_name] = Method(cls, method_func)

  # Return the string representation of this class
  def __str__(cls):
    return cls.typename


######################################
### Definition of the object class ###
######################################

class Obj(metaclass = ObjMeta, typename = "Object"):
  # Get a method in the object
  def get_method(self, name):
    try:
      return self.methods[name].create_callable(self)
    except KeyError:
      raise UndefinedMethodException(name)

  # Set a method in the object
  def set_method(self, name, method):
    self.methods[name] = method

  # Delete a method from the object
  def delete_method(self, name):
    try:
      del self.methods[name]
    except KeyError:
      raise UndefinedMethodException(name)

  # Return if the method with the specified name exists
  def has_method(self, name):
    return name in self.methods

  # Call the method with the specified name
  def call_method(self, name, *args):
    try:
      return self.methods[name].func(self, *args)
    except KeyError:
      raise UndefinedMethodException(name)


  # Return if this object is equal to another object
  def __eq__(self, other):
    return self is other

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return True

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return f"<{self.__class__.typename}>"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the type of this object as a string
  def method_type(self) -> 'ObjString':
    return ObjString(self.__class__.typename)

  # Return the method names of this object as a list of strings
  def method_methods(self) -> 'ObjList':
    from .object_list import ObjList
    return ObjList.from_py(list(self.methods))


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}()"


###########################################
### Definition of the null object class ###
###########################################

class ObjNull(Obj, typename = "Null"):
  # Constructor
  def __init__(self):
    super().__init__()


  # Return if this null object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjNull)

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return False

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return "null"

  def method_as_string(self):
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(None)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())


###########################################
### Definition of the bool object class ###
###########################################

class ObjBool(Obj, typename = "Bool"):
  # Constructor
  def __init__(self, value: 'ObjBool, ObjString') -> 'ObjBool':
    super().__init__()

    if isinstance(value, ObjBool):
      self.value = value.value
    elif isinstance(value, ObjString):
      if value.value == "false":
        self.value = False
      elif value.value == "true":
        self.value = True
      else:
        raise ValueError(f"Unexpected native type {value.__class__.__name__} with value {value!r}")
    elif isinstance(value, bool):
      self.value = value
    elif isinstance(value, str):
      if value == "false":
        self.value = False
      elif value == "true":
        self.value = True
      else:
        raise ValueError(f"Unexpected native type {value.__class__.__name__} with value {value!r}")
    else:
      raise TypeError(f"Unexpected native type {value.__class__.__name__}")


  # Negate the bool object
  def negate(self):
    return ObjBool(not self.value)

  # Return if this bool object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjBool) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return self.value

  def method_asBool(self) -> 'ObjBool':
    return self

  # Return the string representation of this object
  def __str__(self):
    return 'true' if self.value else 'false'

  def method_asString(self):
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())


  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"


#############################################
### Definition of the number object class ###
#############################################

class ObjNumber(Obj, typename = "Number"):
  # Constructor
  def __init__(self):
    super().__init__()


  # Return if this numeric object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjNumber) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.value)

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(bool(self))

  # Return the string representation of this object
  def __str__(self):
    return str(self.value)

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the int representation of this object
  def __int__(self):
    return int(self.value)

  def method_asInt(self) -> 'ObjInt':
    return ObjInt(self.__int__())

  # Return the float representation of this object
  def __float__(self):
    return float(self.value)

  def method_asFloat(self) -> 'ObjFloat':
    return ObjFloat(self.__float__())

  # Compare this number object with another object
  def __lt__(self, other):
    if isinstance(other, ObjNumber):
      return self.value < other.value
    return NotImplemented

  def method_lt(self, other: 'ObjNumber') -> 'ObjBool':
    if (result := self.__lt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __le__(self, other):
    if isinstance(other, ObjNumber):
      return self.value <= other.value
    return NotImplemented

  def method_lte(self, other: 'ObjNumber') -> 'ObjBool':
    if (result := self.__le__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __gt__(self, other):
    if isinstance(other, ObjNumber):
      return self.value > other.value
    return NotImplemented

  def method_gt(self, other: 'ObjNumber') -> 'ObjBool':
    if (result := self.__gt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __ge__(self, other):
    if isinstance(other, ObjNumber):
      return self.value >= other.value
    return NotImplemented

  def method_gte(self, other: 'ObjNumber') -> 'ObjBool':
    if (result := self.__ge__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def method_cmp(self, other: 'ObjNumber') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")


  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"

  # Return a formatted Python representation of this object
  def __format__(self, spec):
    return format(self.value, spec)


##########################################
### Definition of the int object class ###
##########################################

class ObjInt(ObjNumber, typename = "Int"):
  # Constructor
  def __init__(self, value: 'ObjInt, ObjFloat, ObjString' = 0) -> 'ObjInt':
    super().__init__()

    if isinstance(value, ObjInt):
      self.value = value.value
    elif isinstance(value, ObjFloat):
      self.value = int(value.value)
    elif isinstance(value, ObjString):
      try:
        self.value = int(value.value)
      except ValueError:
        raise RuntimeException(f"Invalid int literal {value}")
    elif isinstance(value, int):
      self.value = value
    elif isinstance(value, str):
      try:
        self.value = int(value)
      except ValueError:
        raise RuntimeException(f"Invalid int literal {value}")
    else:
      raise TypeError(f"Unexpected native type {value.__class__.__name__}")


  # Return the addition of two numeric objects
  def __add__(self, other):
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value + other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value + other.value)
    return NotImplemented

  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__add__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value - other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value - other.value)
    return NotImplemented

  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__sub__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value * other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value * other.value)
    return NotImplemented

  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__mul__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumber):
      try:
        return ObjFloat(self.value / other.value)
      except ZeroDivisionError:
        raise RuntimeException("Division by zero")
    return NotImplemented

  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__truediv__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the Python int representation of this object (to avoid deadlocks)
  def __int__(self):
    return self.value


############################################
### Definition of the float object class ###
############################################

# Class that defines a float object
class ObjFloat(ObjNumber, typename = "Float"):
  # Constructor
  def __init__(self, value: 'ObjFloat, ObjInt, ObjString' = 0.0) -> 'ObjFloat':
    super().__init__()

    if isinstance(value, ObjFloat):
      self.value = value.value
    elif isinstance(value, ObjInt):
      self.value = float(value.value)
    elif isinstance(value, ObjString):
      try:
        self.value = float(value.value)
      except ValueError:
        raise RuntimeException(f"Invalid float literal {value}")
    elif isinstance(value, float):
      self.value = value
    elif isinstance(value, int):
      self.value = float(value)
    elif isinstance(value, str):
      try:
        self.value = float(value)
      except ValueError:
        raise RuntimeException(f"Invalid float literal {value}")
    else:
      raise TypeError(f"Unexpected native type {value.__class__.__name__}")


  # Return the addition of two numeric objects
  def __add__(self, other):
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value + other.value)
    return NotImplemented

  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__add__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the suntraction of two numeric objects
  def __sub__(self, other):
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value - other.value)
    return NotImplemented

  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__sub__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the multiplication of two numeric objects
  def __mul__(self, other):
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value * other.value)
    return NotImplemented

  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__mul__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the division of two numeric objects
  def __truediv__(self, other):
    if isinstance(other, ObjNumber):
      try:
        return ObjFloat(self.value / other.value)
      except ZeroDivisionError:
        raise RuntimeException("Division by zero")
    return NotImplemented

  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if (result := self.__truediv__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the Python float representation of this object (to avoid deadlocks)
  def __float__(self):
    return self.value


######################################
### Definition of the string class ###
######################################

# Class that defines a string object
class ObjString(Obj, typename = "String"):
  # Constructor
  def __init__(self, value: 'Obj' = "") -> 'ObjString':
    super().__init__()

    if isinstance(value, ObjString):
      self.value = value.value
    elif isinstance(value, Obj):
      self.value = str(value)
    elif isinstance(value, str):
      self.value = value
    else:
      raise TypeError(f"Unexpected native type {value.__class__.__name__}")


  # Return if this string object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjString) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.value)

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return self.value

  def method_asString(self) -> 'ObjString':
    return self

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this string object to another object
  def __lt__(self, other):
    if isinstance(other, ObjString):
      return self.value < other.value
    return NotImplemented

  def method_lt(self, other: 'ObjString') -> 'ObjBool':
    if (result := self.__lt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __le__(self, other):
    if isinstance(other, ObjString):
      return self.value <= other.value
    return NotImplemented

  def method_lte(self, other: 'ObjString') -> 'ObjBool':
    if (result := self.__le__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __gt__(self, other):
    if isinstance(other, ObjString):
      return self.value > other.value
    return NotImplemented

  def method_gt(self, other: 'ObjString') -> 'ObjBool':
    if (result := self.__gt__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def __ge__(self, other):
    if isinstance(other, ObjString):
      return self.value >= other.value
    return NotImplemented

  def method_gte(self, other: 'ObjString') -> 'ObjBool':
    if (result := self.__ge__(other)) is not NotImplemented:
      return ObjBool(result)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  def method_cmp(self, other: 'ObjString') -> 'ObjInt':
    if self.__eq__(other) == True:
      return ObjInt(0)
    if self.__lt__(other) == True:
      return ObjInt(-1)
    elif self.__gt__(other) == True:
      return ObjInt(1)
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the concatenation of two string objects
  def __add__(self, other):
    if isinstance(other, ObjString):
      return ObjString(self.value + other.value)
    return NotImplemented

  def method_add(self, other: 'ObjString') -> 'ObjString':
    if (result := self.__add__(other)) is not NotImplemented:
      return result
    raise InvalidOperationException(f"Operation 'lt' does not support operands of type {self.__class__} and {other.__class__}")

  # Return the length of this string object
  def __len__(self):
    return len(self.value)

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Return the character in this string object at the specified index
  def __getitem__(self, index):
    if isinstance(index, (ObjInt, int)):
      index = index.value if isinstance(index, ObjInt) else index
      try:
        return ObjString(self.value[index])
      except IndexError:
        raise UndefinedIndexException(index)
    raise InvalidTypeException(f"Method 'at' does not support arguments of type {index.__class__}")

  def method_at(self, index: 'ObjInt') -> 'ObjString':
    return self.__getitem__(index)

  # Return if this string object contains another string object
  def __contains__(self, item):
    if isinstance(item, (ObjString, str)):
      item = item.value if isinstance(item, ObjString) else item
      return ObjBool(self.value.find(item) > -1)
    raise InvalidTypeException(f"Method 'contains' does not support arguments of type {item.__class__}")

  def method_contains(self, item: 'ObjString') -> 'ObjBool':
    return self.__contains__(item)

  # Return if this string object matches a pattern
  def method_match(self, pattern: 'ObjString, ObjRegex') -> 'ObjBool':
    if isinstance(pattern, ObjRegex):
      return ObjBool(pattern.pattern.search(self.value) is not None)
    if isinstance(pattern, ObjString):
      return ObjBool(re.search(pattern.value, self.value, re.IGNORECASE) is not None)
    raise InvalidTypeException(f"Method 'match' does not support arguments of type {pattern.__class__}")


  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"

  # Return the Python string representation of this object (to avoid deadlocks)
  def __str__(self):
    return self.value


############################################
### Definition of the regex object class ###
############################################

class ObjRegex(Obj, typename = "Regex"):
  # Constructor
  def __init__(self, pattern, flags = 0):
    super().__init__()

    if isinstance(pattern, ObjRegex):
      self.pattern = pattern.pattern
    if isinstance(pattern, ObjString):
      self.pattern = re.compile(pattern.value, flags)
    elif isinstance(pattern, re.Pattern):
      self.pattern = pattern
    elif isinstance(pattern, str):
      self.pattern = re.compile(pattern, flags)
    else:
      raise TypeError(f"Unexpected native type {pattern.__class__.__name__}")


  # Return if this regex object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjRegex) and self.pattern == other.pattern

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the string representation of this object
  def __str__(self):
    return f"/{self.pattern.pattern}/{self.flags()}"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the pattern of this regex object
  def method_pattern(self) -> 'ObjString':
    return ObjString(self.pattern.pattern)

  # Return the flags of this regex object:
  def flags(self):
    flags_string = ''
    flags_string += 'i' if self.pattern.flags & re.IGNORECASE else ''
    flags_string += 'm' if self.pattern.flags & re.MULTILINE else ''
    flags_string += 's' if self.pattern.flags & re.DOTALL else ''
    return flags_string

  def method_flags(self) -> 'ObjString':
    return ObjString(self.flags())


  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.pattern!r})"
