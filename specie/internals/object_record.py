import enum

from .object import ObjMeta, Obj, ObjBool, ObjInt, ObjString
from .errors import RuntimeException, UndefinedFieldException


#######################################
### Definition of the field classes ###
#######################################

class FieldOptions(enum.Flag):
  NONE = 0
  PRIVATE = 1 << 0
  FORMAT_ALIGN_RIGHT = 1 << 1
  FORMAT_ELLIPSIS = 1 << 2


class Field:
  # Constructor
  def __init__(self, name, getter = None, setter = None, *, public = True, options = FieldOptions.NONE):
    self.name = name
    self.getter = getter
    self.setter = setter
    self.public = public
    self.options = options

  # Get the value of this field in an instance
  def get(self, instance):
    if self.getter is not None:
      return self.getter(instance)
    else:
      raise RuntimeException(f"The field '{self.name}' is not readable")

  # Set the value of this field in an instance
  def set(self, instance, value):
    if self.setter is not None:
      self.setter(instance, value)
    else:
      raise RuntimeException(f"The field '{self.name}' is not writable")


##################################################
### Definition of the record object meta class ###
##################################################

class ObjRecordMeta(ObjMeta):
  # Class constructor
  def __new__(cls, name, bases, attrs, **kwargs):
    return super().__new__(cls, name, bases, attrs, **kwargs)

  # Class initializer
  def __init__(cls, name, bases, attrs, **kwargs):
    super().__init__(name, bases, attrs, **kwargs)

    # Set the pretty print option of the class
    cls.prettyprint = kwargs.get('prettyprint', True)


#############################################
### Definition of the record object class ###
#############################################

class ObjRecord(Obj, metaclass = ObjRecordMeta, typename = "Record"):
  # Constructor
  def __init__(self, **fields):
    super().__init__()
    super().__setattr__('fields', {})


  # Declare a property field in the record
  def declare_delegate(self, name, getter, setter = None, location = None, **kwargs):
    if self.has_field(name):
      raise RuntimeException(f"The field {name} already exists", location)

    self.fields[name] = field = Field(name, getter, setter, **kwargs)
    setattr(self.__class__, name, property(field.get, field.set))

  # Declare a value field in the record
  def declare_field(self, name, value, mutable = True, location = None, **kwargs):
    def getter(self):
      return self.__dict__[f'__{name}']
    def setter(self, value):
      self.__dict__[f'__{name}'] = value

    self.declare_delegate(name, getter, setter if mutable else None, location, **kwargs)
    setter(self, value)

  # Get a field in the record object
  def get_field(self, name, location = None):
    if self.has_field(name):
      return self.fields[name].get(self)
    else:
      raise UndefinedFieldException(name, location)

  def __getattr__(self, name):
    try:
      return self.get_field(name)
    except UndefinedFieldException:
      raise AttributeError(name)

  # Get a field in the record object, or a default variable if it doesn't exist
  def get_field_or(self, name, default = None):
    try:
      return self.get_field(name)
    except UndefinedFieldException:
      return default

  # Set a field in the record object
  def set_field(self, name, value, location = None):
    if self.has_field(name):
      self.fields[name].set(self, value)
    else:
      raise UndefinedFieldException(name, location)

  def __setattr__(self, name, value):
    if self.has_field(name):
      self.set_field(name, value)
    else:
      super().__setattr__(name, value)

  # Return if a field exists in the record object
  def has_field(self, name):
    return name in self.fields


  # Iterate over the fields and their values in the record object
  def __iter__(self):
    for name in self.fields:
      yield name, self.get_field(name)


  # Return the string representation of this object
  def __str__(self):
    return '{' + ', '.join(f"{name}: {value}" for name, value in self) + '}'

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())
