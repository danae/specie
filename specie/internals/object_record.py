from enum import Flag

from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException, UndefinedFieldException


# Class that defines options for a field
class ObjRecordFieldOptions(Flag):
  NONE = 0
  FORMAT_RIGHT = 1 << 0
  FORMAT_ELLIPSIS = 1 << 1


# Class that defines info for a field
class ObjRecordFieldInfo:
  # Constructor
  def __init__(self, mutable = True, visible = True, options = ObjRecordFieldOptions.NONE):
    self.mutable = mutable
    self.visible = visible
    self.options = options


# Class that defines a record object
class ObjRecord(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)
    self.fields = {}
    self.fields_info = {}


  ### Definition of field access functions ###

  # Get a field in the record
  def __getitem__(self, name):
    return self.fields[name]

  # Set a field in the record
  def __setitem__(self, name, value):
    if isinstance(value, tuple):
      value, *info = value
      self.fields_info[name] = ObjRecordFieldInfo(*info)
    self.fields[name] = value

  # Return if a field exists in the record
  def __contains__(self, name):
    return name in self.fields

  # Return an iterator over the fields in the record
  def __iter__(self):
    return iter(self.fields.items())

  # Return an iterator over the field names in the record
  def names(self, *, only_mutable = False, only_visible = False):
    for name in self.fields:
      info = self.info(name)
      if (not only_mutable or info.mutable) and (not only_visible or info.visible):
        yield name

  # Return a field in the record, or a default value if the field doesn't exist
  def get(self, name, default = None):
    try:
      return self[name]
    except IndexError:
      return default

  # Return the info for a field in the record
  def info(self, name):
    if name not in self.fields_info:
      self.fields_info[name] = ObjRecordFieldInfo()
    return self.fields_info[name]


  ### Definition of field access functions for lexer tokens ###

  # Get a field in the record by means of a lexer token
  def get_field(self, name):
    try:
      return self[name.value]
    except IndexError:
      raise UndefinedFieldException(name.value, name.location)

  # Set a field in the record by means of a lexer token
  def set_field(self, name, value):
    self[name.value] = value

  # Return if a field with the specified name exists
  def has_field(self, name):
    return name.value in self


  ### Definition of object functions ###

  # Return the primitive value of this object
  def value(self):
    return {name: value.value() for name, value in self.fields.items()}

  # Return the truthiness of this object
  def truthy(self):
    return ObjBool(bool(self.fields))

  # Return if this record object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjRecord) and self.fields == other.fields)


  ### Definition of conversion functions ###

  # Convert to hash
  def __hash__(self):
    return hash((self.fields))

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.fields!r})"

  # Convert to string
  def __str__(self):
    return '{' + ', '.join(f"{name}: {value}" for name, value in self.fields.items()) + '}'
