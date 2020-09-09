import functools

from .errors import UndefinedMethodException


# Base class for any object
class Obj:
  # Constructor
  def __init__(self):
    self.methods = {}
    self.set_method('eq', self.__eq__)


  ### Definition of method functions ###

  # Return if a method with the specified name exists
  def has_method(self, name):
    return name in self.methods

  # Set the method with the specified name and function
  def set_method(self, name, func):
    self.methods[name] = func

  # Return the method with the specified name
  def get_method(self, name):
    if not self.has_method(name):
      raise UndefinedMethodException(name)
    return self.methods[name]

  # Remove the method with the specified name
  def remove_method(self, name):
    if not self.has_method(name):
      raise UndefinedMethodException(name)
    del self.methods[name]

  # Iterate over the methods names in this record
  def iter_methods(self):
    yield from self.methods

  # Call the method with the specified name
  def call(self, name, *arguments):
    return self.get_method(name)(*arguments)


  ### Definition of object functions

  # Return the primitive value of this object
  def value(self):
    return None

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(True)

  # Return if this object is equal to another object
  def __eq__(self, other):
    return ObjBool(self is other)


  ### Definition of conversion functions ###

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}()"

  # Convert to string
  def __str__(self):
    return "<object>"


# Class that defines a null object
class ObjNull(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)


  ### Definition of object functions ###

  # Return the primitive value of this object
  def value(self):
    return None

  # Return the thruthiness of this object
  def truthy(self):
    return ObjBool(False)

  # Return if this null object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjNull)


  ### Definition of conversion functions ###

  # Convert to string
  def __str__(self):
    return "null"


# Class that defines a bool object
class ObjBool(Obj):
  # Constructor
  def __init__(self, bool_value):
    Obj.__init__(self)

    if isinstance(bool_value, ObjBool):
      self.bool_value = bool_value.value()
    elif isinstance(bool_value, bool):
      self.bool_value = bool_value
    elif value == "false":
      self.bool_value = False
    elif value == "true":
      self.bool_value = True
    else:
      raise TypeError(type(bool_value))


  ### Definition of object functions ###

  # Return the primitive value of this object
  def value(self):
    return self.bool_value

  # Return the thruthiness of this object
  def truthy(self):
    return self

  # Return if this bool object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjBool) and self.bool_value == other.bool_value)


  ### Definition of conversion functions

  # Convert to bool
  def __bool__(self):
    return self.bool_value

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.bool_value!r})"

  # Convert to string
  def __str__(self):
    return 'true' if self.bool_value else 'false'
