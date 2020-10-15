from bisect import insort

from .object import Obj, ObjNull, ObjBool, ObjInt, ObjString
from .object_iterable import ObjIterable, ObjIterator
from .object_list import ObjList
from .object_record import ObjRecord
from .errors import InvalidStateException, InvalidTypeException, UndefinedKeyException


##########################################
### Definition of the map object class ###
##########################################

class ObjMap(ObjIterable, typename = "Map"):
  # Constructor
  def __init__(self):
    super().__init__()
    self.elements = {}


  # Return if this map object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjList) and self.elements == other.elements

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.elements)

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    elements = ', '.join(f"{key} = {value}" for key, value in self.elements.items()) if self.elements else "empty"
    return f"<{self.__class__.typename}: " + elements + ">"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Get a value in the map object
  def get(self, key, default = None):
    if key in self.elements:
      return self.elements[key]
    elif default is not None:
      return default
    else:
      raise UndefinedKeyException(key)

  def method_get(self, key: 'Obj', default: 'Obj' = None) -> 'Obj':
    return self.get(key, default)

  # Set a value in the map object
  def set(self, key, value):
    if not hasattr(key, '__hash__'):
      raise InvalidTypeException(f"Maps don't support unhashable keys of type {key.__class__}")
    self.elements[key] = value

  def method_set(self, key: 'Obj', value: 'Obj') -> 'ObjMap':
    self.set(key, value)
    return self

  # Delete a value in the map object
  def delete(self, key):
    if key in self.elements:
      del self.elements[key]
    return self

  def method_delete(self, key: 'Obj') -> 'ObjMap':
    self.delete(key)
    return self

  # Return an iterator for the map object
  def __iter__(self):
    return ObjMapIterator(self)

  def method_iterator(self) -> 'ObjIterator':
    return self.__iter__()

  # Return if a value exists in the map object
  def __contains__(self, key):
    return key in self.elements

  def method_contains(self, key: 'Obj') -> 'ObjBool':
    return self.__contains__(key)

  # Return the length of the map object
  def __len__(self):
    return len(self.elements)

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Return the keys in the map object
  def method_keys(self) -> 'ObjList':
    return ObjList(*list(self.elements))

  # Return the keys in the map object
  def method_values(self) -> 'ObjList':
    return ObjList(*self.elements.values())


##################################################
### Definition of the map element object class ###
##################################################

class ObjMapElement(ObjRecord, typename = "MapElement", prettyprint = False):
  # Constructor
  def __init__(self, map, key):
    super().__init__()
    super().__setattr__('_map', map)
    super().__setattr__('_key', key)

    self.declare_delegate('key', lambda self: self._key)
    self.declare_delegate('value', lambda self: self._map.get(self._key), lambda self, value: self._map.set(self._key, value))


  # Return if this map element object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjMapElement) and (self._map, self._key) == (other._map, other._key)

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the string representation of this object
  def __str__(self):
    return f"{self.key} = {self.value}"

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())


###################################################
### Definition of the map iterator object class ###
###################################################

class ObjMapIterator(ObjIterator, typename = "MapIterator"):
  # Constructor
  def __init__(self, map):
    super().__init__()

    self.map = map
    self.map_keys = list(map.elements)
    self.map_keys_index = None
    self.map_keys_deleted = False


  # Return the element at the cursor of the iterator object
  def current(self):
    if self.map_keys_index is None or self.map_keys_deleted:
      raise InvalidStateException("The iterator has not yet been advanced")
    else:
      return ObjMapElement(self.map, self.map_keys[self.map_keys_index])

  # Advance the cursor of the iterator object
  def advance(self):
    if self.map_keys_index is None:
      self.map_keys_index = 0
    elif self.map_keys_deleted:
      self.map_keys_deleted = False
    else:
      self.map_keys_index += 1
    return self.map_keys_index < len(self.map_keys)

  # Rewind the iterator object
  def rewind(self):
    self.map_keys_index = None

  # Delete the element at the cursor of the iterator object
  def delete(self):
    if self.map_keys_index is None or self.map_keys_deleted:
      raise InvalidStateException("The iterator has not yet been advanced")
    else:
      self.map.delete(self.map_keys[self.map_keys_index])
      del self.map_keys[self.map_keys_index]
      self.map_keys_deleted = True
