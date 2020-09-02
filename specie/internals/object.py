import functools

from .errors import UndefinedMethod


# Base class for any object
class Obj:
  # Constructor
  def __init__(self):
    self.methods = {}

    self.set_method('eq', self.__eq__)

  # Return if a method with the specified name exists
  def has_method(self, name):
    return name in self.methods

  # Set the method with the specified name and function
  def set_method(self, name, func):
    self.methods[name] = func

  # Return the method with the specified name
  def get_method(self, name):
    if not self.has_method(name):
      raise UndefinedMethod(name)
    return self.methods[name]

  # Remove the method with the specified name
  def remove_method(self, name):
    if not self.has_method(name):
      raise UndefinedMethod(name)
    del self.methods[name]

  # Iterate over the methods names in this record
  def iter_methods(self):
    yield from self.methods

  # Call the method with the specified name
  def call(self, name, *arguments):
    return self.get_method(name)(*arguments)

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(True)

  # Return if this object is equal to another object
  def __eq__(self, other):
    return ObjBool(self is other)

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}()"

  # Convert to string
  def __str__(self):
    return "object"


# Class that defines a null object
class ObjNull(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(False)

  # Return if this null object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjNull)

  # Convert to string
  def __str__(self):
    return "null"


# Class that defines a bool object
class ObjBool(Obj):
  # Constructor
  def __init__(self, value):
    Obj.__init__(self)

    if isinstance(value, ObjBool):
      self.value = value.value
    elif isinstance(value, bool):
      self.value = value
    elif value == "false":
      self.value = False
    elif value == "true":
      self.value = True
    else:
      raise TypeError(type(value))

  # Return the thruthiness of this object
  def truthy(self):
    return self

  # Return if this bool object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjBool) and self.value == other.value)

  # Convert to hash
  def __hash__(self):
    return hash((self.value))

  # Convert to bool
  def __bool__(self):
    return self.value

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"

  # Convert to string
  def __str__(self):
    return 'true' if self.value else 'false'
