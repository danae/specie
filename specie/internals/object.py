import functools
import importlib
import inspect
import re
import sys
import types

from .errors import UndefinedMethodException, UndefinedIndexException


######################################
### Definition of the method class ###
######################################

class Method:
  # Constructor
  def __init__(self, func, required_args, required_kwargs):
    self.func = func
    self.required_args = required_args
    self.required_kwargs = required_kwargs

  # Resolve the method to a callable
  def create_callable(self, this_arg):
    from .object_callable import ObjNativeCallable

    callable = ObjNativeCallable(self.func, self.required_args, self.required_kwargs)
    callable = callable.bind(this_arg)
    return callable


###########################################
### Definition of the object meta class ###
###########################################

class ObjMeta(type):
  # Dict that holds all defined classes
  obj_classes = {}

  # Class constructor
  def __new__(cls, name, bases, attrs, **kwargs):
    return super(ObjMeta, cls).__new__(cls, name, bases, attrs)

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

      signature = inspect.signature(method_func)
      required_args = [cls.resolve(param) for param in signature.parameters.values() if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]]
      required_kwargs = {name: cls.resolve(param) for param in signature.parameters.values() if param.kind == inspect.Parameter.KEYWORD_ONLY}

      cls.methods[method_name] = Method(method_func, required_args, required_kwargs)

  # Return a parameter resolved to a class
  @classmethod
  def resolve(cls, param):
    if param.name == "self":
      return cls
    elif param.annotation == inspect.Parameter.empty:
      return cls.obj_classes['Obj']
    else:
      return tuple(cls.obj_classes[annot.strip()] for annot in param.annotation.split(','))


######################################
### Definition of the object class ###
######################################

class Obj(metaclass = ObjMeta, typename = "Object"):
  # Constructor
  def __init__(self):
    pass


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
  def call_method(self, name, *args, **kwargs):
    try:
      return self.methods[name].func(self, *args, **kwargs)
    except KeyError:
      raise UndefinedMethodException(name)


  # Return if this object is equal to another object
  def __eq__(self, other):
    return self is other

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return if this object is not equal to another object
  def __ne__(self, other):
    return not self.__eq__(other)

  def method_neq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__ne__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return True

  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return f"<{self.__class__.typename}>"

  def method_as_string(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return id(self)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the defined methods of this object
  def method_methods(self) -> 'ObjRecord':
    from .object_record import ObjRecord
    return ObjRecord(**{name: method.create_callable(self) for name, method in self.methods.items()})


  # Overload functions for equality testing
  #def __eq__(self, other):
  #  return bool(self.call_method('eq', other))
  #def __ne__(self, other):
  #  return bool(self.call_method('neq', other))

  # Overload functions for truth value testing
  #def __bool__(self):
  #  return bool(self.call_method('as_bool'))

  # Overload functions for object properties
  #def __str__(self):
  #  return str(self.call_method('as_string'))
  #def __hash__(self):
  #  return int(self.call_method('as_hash'))

  # Overload functions for conversions
  #def __int__(self):
  #  return int(self.call_method('as_int')) if self.has_method('as_int') else NotImplemented
  #def __float__(self):
  #  return float(self.call_method('as_float')) if self.has_method('as_float') else NotImplemented

  # Overload functions for comparison operators
  #def __lt__(self, other):
  #  return bool(self.call_method('lt', other)) if self.has_method('lt') else NotImplemented
  #def __le__(self, other):
  #  return bool(self.call_method('lte', other)) if self.has_method('lte') else NotImplemented
  #def __gt__(self, other):
  #  return bool(self.call_method('gt', other)) if self.has_method('gt') else NotImplemented
  #def __ge__(self, other):
  #  return bool(self.call_method('gte', other)) if self.has_method('gte') else NotImplemented

  # Overload functions for arithmetic operators
  def __add__(self, other):
    return self.call_method('add', other) if self.has_method('add') else NotImplemented
  def __sub__(self, other):
    return self.call_method('sub', other) if self.has_method('sub') else NotImplemented
  def __mul__(self, other):
    return self.call_method('mul', other) if self.has_method('mul') else NotImplemented
  def __truediv__(self, other):
    return self.call_method('div', other) if self.has_method('div') else NotImplemented

  # Overload functions for container operators
  def __len__(self):
    return int(self.call_method('count')) if self.has_method('count') else NotImplemented
  def __contains__(self, other):
    return bool(self.call_method('contains', other)) if self.has_method('contains') else NotImplemented


  # Return the Python value of this object (empty for standard objects)
  def _py_value(self):
    return None

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
  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return isinstance(other, ObjNull)

  # Return the bool representation of this object
  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(False)

  # Return the string representation of this object
  def method_as_string(self):
    return "null"


###########################################
### Definition of the bool object class ###
###########################################

class ObjBool(Obj, typename = "Bool"):
  # Constructor
  def __init__(self, value):
    super().__init__()

    if isinstance(value, ObjBool):
      self.value = value.value
    elif isinstance(value, bool):
      self.value = value
    elif value == "false":
      self.value = False
    elif value == "true":
      self.value = True
    else:
      raise TypeError(f"Unexpected native type {type(value)}")


  # Return if this bool object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjBool) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return self.value

  def method_as_bool(self) -> 'ObjBool':
    return self

  # Return the string representation of this object
  def __str__(self):
    return 'true' if self.value else 'false'

  def method_as_string(self):
    return ObjString(self.__str__())


  # Return the Python value of this object
  def _py_value(self):
    return self.value

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

  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(bool(self))

  # Return the string representation of this object
  def __str__(self):
    return str(self.value)

  def method_as_string(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the int representation of this object
  def __int__(self):
    return int(self.value)

  def method_as_int(self) -> 'ObjInt':
    return ObjInt(self.__int__())

  # Return the float representation of this object
  def __float__(self):
    return float(self.value)

  def method_as_float(self) -> 'ObjFloat':
    return ObjFloat(self.__float__())

  # Compare this number object with another object
  def __lt__(self, other):
    if isinstance(other, ObjNumber):
      return self.value < other.value
    raise InvalidTypeException(other)

  def method_lt(self, other: 'ObjNumber') -> 'ObjBool':
    return ObjBool(self.__lt__(other))

  def __le__(self, other):
    if isinstance(other, ObjNumber):
      return self.value <= other.value
    raise InvalidTypeException(other)

  def method_lte(self, other: 'ObjNumber') -> 'ObjBool':
    return ObjBool(self.__le__(other))

  def __gt__(self, other):
    if isinstance(other, ObjNumber):
      return self.value > other.value
    raise InvalidTypeException(other)

  def method_gt(self, other: 'ObjNumber') -> 'ObjBool':
    return ObjBool(self.__gt__(other))

  def __ge__(self, other):
    if isinstance(other, ObjNumber):
      return self.value >= other.value
    raise InvalidTypeException(other)

  def method_gte(self, other: 'ObjNumber') -> 'ObjBool':
    return ObjBool(self.__ge__(other))


  # Return the Python value of this object
  def _py_value(self):
    return self.value

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
  def __init__(self, value = 0):
    super().__init__()

    if isinstance(value, ObjInt):
      self.value = value.value
    elif isinstance(value, ObjFloat):
      self.value = int(value.value)
    elif isinstance(value, Obj) and value.has_method('as_int'):
      self.value = int(value.call_method('as_int'))
    elif isinstance(value, int):
      self.value = value
    elif isinstance(value, str):
      self.value = int(value)
    else:
      raise TypeError(f"Unexpected native type {type(value)}")


  # Return the addition of two numeric objects
  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value + other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value + other.value)
    raise InvalidTypeException(other)

  # Return the suntraction of two numeric objects
  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value - other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value - other.value)
    raise InvalidTypeException(other)

  # Return the multiplication of two numeric objects
  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjFloat):
      return ObjFloat(self.value * other.value)
    elif isinstance(other, ObjInt):
      return ObjInt(self.value * other.value)
    raise InvalidTypeException(other)

  # Return the division of two numeric objects
  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value / other.value)
    raise InvalidTypeException(other)

  # Return the Python int representation of this object (to avoid deadlocks)
  def __int__(self):
    return self.value


############################################
### Definition of the float object class ###
############################################

# Class that defines a float object
class ObjFloat(ObjNumber, typename = "Float"):
  # Constructor
  def __init__(self, value = 0.0):
    super().__init__()

    if isinstance(value, ObjFloat):
      self.value = value.value
    elif isinstance(value, ObjInt):
      self.value = float(value.value)
    elif isinstance(value, Obj) and value.has_method('as_float'):
      self.value = float(value.call_method('as_float'))
    elif isinstance(value, float):
      self.value = value
    elif isinstance(value, int):
      self.value = float(value)
    elif isinstance(value, str):
      self.value = float(value)
    else:
      raise TypeError(f"Unexpected native type {type(value)}")


  # Return the addition of two numeric objects
  def method_add(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value + other.value)
    raise InvalidTypeException(other)

  # Return the suntraction of two numeric objects
  def method_sub(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value - other.value)
    raise InvalidTypeException(other)

  # Return the multiplication of two numeric objects
  def method_mul(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value * other.value)
    raise InvalidTypeException(other)

  # Return the division of two numeric objects
  def method_div(self, other: 'ObjNumber') -> 'ObjNumber':
    if isinstance(other, ObjNumber):
      return ObjFloat(self.value / other.value)
    raise InvalidTypeException(other)

  # Return the Python float representation of this object (to avoid deadlocks)
  def __float__(self):
    return self.value


######################################
### Definition of the string class ###
######################################

# Class that defines a string object
class ObjString(Obj, typename = "String"):
  # Constructor
  def __init__(self, value = ""):
    super().__init__()

    if isinstance(value, ObjString):
      self.value = value.value
    elif isinstance(value, Obj) and value.has_method('as_string'):
      self.value = str(value)
    elif isinstance(value, str):
      self.value = value
    else:
      raise TypeError(f"Unexpected native type {type(value)}")


  # Return if this string object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjString) and self.value == other.value

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.value)

  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return self.value

  def method_as_string(self) -> 'ObjString':
    return self

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this string object to another object
  def __lt__(self, other):
    if isinstance(other, ObjString):
      return self.value < other.value
    raise InvalidTypeException(other)

  def method_lt(self, other: 'ObjString') -> 'ObjBool':
    return ObjBool(self.__lt__(other))

  def __le__(self, other):
    if isinstance(other, ObjString):
      return self.value <= other.value
    raise InvalidTypeException(other)

  def method_lte(self, other: 'ObjString') -> 'ObjBool':
    return ObjBool(self.__le__(other))

  def __gt__(self, other):
    if isinstance(other, ObjString):
      return self.value > other.value
    raise InvalidTypeException(other)

  def method_gt(self, other: 'ObjString') -> 'ObjBool':
    return ObjBool(self.__gt__(other))

  def __ge__(self, other):
    if isinstance(other, ObjString):
      return self.value >= other.value
    raise InvalidTypeException(other)

  def method_gte(self, other: 'ObjString') -> 'ObjBool':
    return ObjBool(self.__ge__(other))

  # Return the concatenation of two string objects
  def method_add(self, other: 'ObjString') -> 'ObjString':
    if isinstance(other, ObjString):
      return ObjString(self.value + other.value)
    raise InvalidTypeException(pattern)

  # Return the length of this string object
  def method_count(self) -> 'ObjInt':
    return ObjInt(len(self.value))

  # Return the character in this string object at the specified index
  def method_at(self, index: 'ObjInt') -> 'ObjString':
    if isinstance(index, ObjInt):
      try:
        return ObjString(self.value[index.value])
      except IndexError:
        raise UndefinedIndexException(index)
    raise InvalidTypeException(index)

  # Return a slice of this string object
  def method_slice(self, start: 'ObjInt', end: 'ObjInt') -> 'ObjString':
    if isinstance(start, ObjInt):
      if isinstance(end, ObjInt):
        return ObjString(self.value[start.value:end.value])
      raise InvalidTypeException(end)
    raise InvalidTypeException(start)

  # Return if this string object contains another string object
  def method_contains(self, sub: 'ObjString') -> 'ObjBool':
    if isinstance(sub, ObjString):
      return ObjBool(self.value.find(sub.value) > -1)
    raise InvalidTypeException(sub)

  # Return if this string object matches a pattern
  def method_match(self, pattern: 'Obj') -> 'ObjBool':
    if isinstance(pattern, ObjRegex):
      return ObjBool(pattern.pattern.search(self.value) is not None)
    if isinstance(pattern, ObjString):
      return ObjBool(re.search(pattern.value, self.value, re.IGNORECASE) is not None)
    raise InvalidTypeException(pattern)


  # Return the Python value of this object
  def _py_value(self):
    return self.value

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
  def __init__(self, pattern):
    super().__init__()

    if isinstance(pattern, ObjString):
      self.pattern = re.compile(pattern.value, re.IGNORECASE)
    elif isinstance(pattern, str):
      self.pattern = re.compile(pattern, re.IGNORECASE)
    else:
      raise TypeError(f"Unexpected native type {type(pattern)}")

  # Return if this regex object is equal to another object
  def __eq__(self):
    return isinstance(other, ObjRegex) and self.pattern == other.pattern

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the string representation of this object
  def __str__(self):
    return f"regex \"{self.pattern.pattern}\""

  def method_as_string(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.pattern)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the pattern of this regex object
  def method_pattern(self) -> 'ObjString':
    return ObjString(self.pattern.pattern)


  # Return the Python value of this object
  def _py_value(self):
    return self.pattern

  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.pattern!r})"
