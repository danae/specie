from .object import Obj, ObjNull, ObjBool
from .errors import InvalidTypeException, UndefinedField


# Class that defines a record object
class ObjRecord(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)

    self.fields = {}

  # Return if a field with the specified name exists
  def has_field(self, name):
    return name in self.fields

  # Set the field with the specified name and value
  def set_field(self, name, value):
    self.fields[name] = value

  # Return the field with the specified name
  def get_field(self, name):
    if not self.has_field(name):
      raise UndefinedField(name)
    return self.fields[name]

  # Return the field with the specified name, or a default value if the field is undefined
  def get_field_or_default(self, name, default = None):
    try:
      return self.get_field(name)
    except UndefinedField:
      return default

  # Remove the field with the specified name
  def remove_field(self, name):
    if not self.has_field(name):
      raise UndefinedField(name)
    del self.fields[name]

  # Iterate over the field names in this record
  def iter_fields(self):
    yield from self.fields

  # Return the truthiness of this object
  def truthy(self):
    return ObjBool(bool(self.fields))

  # Return if this record object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjRecord) and self.fields == other.fields)

  # Convert to hash
  def __hash__(self):
    return hash((self.fields))

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.fields!r})"

  # Convert to string
  def __str__(self):
    return '{' + ', '.join(f"{name}: {value}" for name, value in self.fields.items()) + '}'
