from enum import Flag

from .object import Obj, ObjBool, ObjInt, ObjString
from .object_list import ObjList
from .errors import InvalidTypeException, UndefinedFieldException


############################################
### Definition of the record field class ###
############################################

class FieldOptions(Flag):
  NONE = 0
  FORMAT_ALIGN_RIGHT = 1 << 0
  FORMAT_ELLIPSIS = 1 << 1

class Field:
  # Constructor
  def __init__(self, value, *, mutable = True, public = True, options = FieldOptions.NONE):
    self.value = value
    self.mutable = mutable
    self.public = public
    self.options = options

  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value}, mutable={self.mutable}, public={self.public}, options={self.options})"



#############################################
### Definition of the record object class ###
#############################################

class ObjRecord(Obj, typename = "Record"):
  # Constructor
  def __init__(self, **fields):
    super().__init__()

    self.fields = {}

    for name, value in fields.items():
      self[name] = value


  # Get a field in the record
  def get_field(self, name):
    try:
      return self.fields[name].value
    except IndexError:
      raise UndefinedFieldException(name)

  # Set a field in the record
  def set_field(self, name, value):
    if isinstance(value, Field):
      self.fields[name] = value
    elif self.has_field(name):
      self.fields[name].value = value
    else:
      self.fields[name] = Field(value)

  # Delete a field in the record
  def delete_field(self, name):
    try:
      del self.fields[name]
    except IndexError:
      raise UndefinedFieldException(name)

  #  Return if a field exists in the record
  def has_field(self, name):
    return name in self.fields


  # Return if this record object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjRecord) and self.fields == other.fields

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.fields)

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return '{' + ', '.join(f"{name}: {field.value}" for name, field in self.fields.items()) + '}'

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this objet
  def __hash__(self):
    return hash(self.fields)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Get the field with the specified name in this record object
  def __getitem__(self, name):
    if isinstance(name, (ObjString, str)):
      name = name.value if isinstance(name, ObjString) else name
      return self.get_field(name)
    raise InvalidTypeException(name)

  def method_get(self, name: 'ObjString') -> 'Obj':
    return self.__getitem__(name)

  # Set the field with the specified name in this record object to a value
  def __setitem__(self, name, value):
    if isinstance(name, (ObjString, str)):
      name = name.value if isinstance(name, ObjString) else name
      self.set_field(name, value)
      return
    raise InvalidTypeException(name)

  def method_set(self, name: 'ObjString', value: 'Obj') -> 'ObjRecord':
    self.__setitem__(name, value)
    return self

  # Delete the field with the specified name from this record object
  def __delitem__(self, name):
    if isinstance(name, (ObjString, str)):
      name = name.value if isinstance(name, ObjString) else name
      self.delete_field(name)
      return
    raise InvalidTypeException(name)

  def method_delete(self, name: 'ObjString') -> 'ObjRecord':
    self.__delitem__(name)
    return self

  # Return if this record object contains a field with the specified name
  def __contains__(self, name):
    if isinstance(name, (ObjString, str)):
      name = name.value if isinstance(name, ObjString) else name
      return self.has_field(name)
    raise InvalidTypeException(name)

  def method_contains(self, name: 'ObjString') -> 'ObjBool':
    return self.__contains__(name)

  # Return the field object with the specified name from this record object
  def field(self, name):
    return self.fields.get(name, None)

  # Return the field balue with the specified name from this record object
  def field_value(self, name, default = None):
    return field.value if (field := self.fields.get(name, None)) is not None else default

  # Return the fields of this record as a dict
  def list_fields(self, *, only_mutable = False, only_public = False):
    fields = {}
    for name, field in self.fields.items():
      if (not only_mutable or field.mutable) and (not only_public or field.public):
        fields[name] = field
    return fields

  # Return the field values of this record as a dict
  def list_field_values(self, *, only_mutable = False, only_public = False):
    return {name: field.value for name, field in self.list_fields(only_mutable = only_mutable, only_public = only_public).items()}

  # Return the field names of this record object as a list of strings
  def list_field_names(self, *, only_mutable = False, only_public = False):
    return list(self.list_fields(only_mutable = only_mutable, only_public = only_public))

  def method_fields(self) -> 'ObjList':
    return ObjList.from_py(self.list_field_names())


  # Return the Python value for this object
  def _py_value(self):
    return {name: field.value._py_value() for name, field in self.fields.items()}

  # Return the Python dict for this object
  def _py_dict(self):
    return {name: field.value for name, field in self.fields.items()}

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}(**{self.fields!r})"

  # Return a Python iterator for this object
  def __iter__(self):
    return iter(self.list_field_values().items())


  # Convert a Python dict to a record object
  @classmethod
  def from_py(cls, dict):
    return cls(**dict)
