from enum import Flag

from .object import Obj, ObjBool, ObjInt, ObjString
from .errors import InvalidTypeException, UndefinedFieldException


############################################
### Definition of record object helpeers ###
############################################

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


#############################################
### Definition of the record object class ###
#############################################

# Class that defines a record object
class ObjRecord(Obj, typename = "Record"):
  # Constructor
  def __init__(self, **fields):
    super().__init__()

    self.fields = {}
    self.fields_info = {}

    for name, value in fields.items():
      self[name] = value


  # Get a field in the record
  def __getitem__(self, name):
    return self.fields[name]

  # Set a field in the record
  def __setitem__(self, name, value):
    if isinstance(value, tuple):
      value, *info = value
      self.fields_info[name] = ObjRecordFieldInfo(*info)
    self.fields[name] = value

  # Delete a field from the record
  def __delitem__(self, name):
    del self.fields[name]

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

  # Get a field in the record
  def get_field(self, name):
    try:
      return self[name]
    except KeyError:
      raise UndefinedFieldException(name.value, name.location)

  # Set a field in the record
  def set_field(self, name, value):
    self[name] = value

  # Delete a field from the record
  def delete_field(self, name):
    del self[name]

  # Return if a field with the specified name exists
  def has_field(self, name):
    return name in self


  # Return if this record object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjRecord) and self.fields == other.fields

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.fields)

  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return '{' + ', '.join(f"{name}: {value}" for name, value in self.fields.items()) + '}'

  def method_as_string(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this objet
  def __hash__(self):
    return hash(self.fields)

  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the field in this record object with the specified name
  def method_get(self, name: 'ObjString') -> 'Obj':
    return self[name.value]

  # Set the field in this record object with the specified name to a value
  def method_set(self, name: 'ObjString', value: 'Obj') -> 'Obj':
    self[name.value] = value
    return value

  # Return if this record object contains a field with the specified name
  def method_contains(self, name: 'ObjString') -> 'ObjBool':
    return name.value in self


  # Return the Python value for this object
  def _py_value(self):
    return {name: value._py_value() for name, value in self.fields.items()}

  # Return the Python dict for this object
  def _py_dict(self):
    return self.fields

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}(**{self.fields!r})"


  # Convert a Python dict to a record object
  @classmethod
  def from_py(cls, dict):
    return cls(**dict)
