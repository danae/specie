from bisect import insort

from .object import Obj, ObjBool, ObjInt, ObjString
from .errors import InvalidTypeException, UndefinedIndexException

###########################################
### Definition of the list object class ###
###########################################

class ObjList(Obj, typename = "List"):
  # Constructor
  def __init__(self, *items):
    super().__init__()

    self.items = []
    self.insert_all(items)


  # Return if this list object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjList) and self.items == other.items

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the bool representation of this object
  def __bool__(self):
    return bool(self.items)

  def method_asBool(self) -> 'ObjBool':
    return ObjBool(self.__bool__())

  # Return the string representation of this object
  def __str__(self):
    return '[' + ', '.join(f"{item}" for item in self.items) + ']'

  def method_asString(self) -> 'ObjString':
    return ObjString(self.__str__())

  # Return the hash of this object
  def __hash__(self):
    return hash(self.value)

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Return the length of this list object
  def __len__(self):
    return len(self.items)

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Return the item in this list object at the specified index
  def __getitem__(self, index):
    if isinstance(index, ObjInt):
      try:
        return self.items[index.value]
      except IndexError:
        raise UndefinedIndexException(index)
    raise InvalidTypeException(type(index))

  def method_at(self, index: 'ObjInt') -> 'Obj':
    return self.__getitem__(index)

  # Return if this list object contains the specified item
  def __contains__(self, item):
    return item in self.items

  def method_contains(self, item: 'Obj') -> 'ObjBool':
    return ObjBool(self.__contains__(item))

  # Insert an item into this list object
  def insert(self, item):
    self.items.append(item)

  def method_insert(self, item: 'Obj') -> 'ObjList':
    self.insert(item)
    return self

  # Insert several items into this list object
  def insert_all(self, list):
    for item in list:
      self.insert(item)

  def method_insertAll(self, list: 'ObjList') -> 'ObjList':
    self.insert_all(list)
    return self

  # Delete an item from this list object
  def delete(self, item):
    try:
      self.items.remove(item)
    except ValueError:
      pass

  def method_delete(self, item: 'Obj') -> 'ObjList':
    self.delete(item)
    return self

  # Map the items of the list
  def map(self, func):
    return ObjList.from_py(func(item) for item in self)

  def method_map(self, func: 'ObjCallable') -> 'ObjList':
    return self.map(func)

  # Filter the items of the list
  def filter(self, func):
    return ObjList.from_py(item for item in self if func(item))

  def method_filter(self, func: 'ObjCallable') -> 'ObjList':
    return self.filter(func)


  # Return the Python value for this object
  def _py_value(self):
    return [value._py_value() for value in self.items]

  # Return the Python list for this object
  def _py_list(self):
    return self.items

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}(*{self.items!r})"

  # Convert to iterator
  def __iter__(self):
    return iter(self.items)


  # Convert a Python iterable to a list object
  @classmethod
  def from_py(cls, iterable):
    return cls(*iterable)


##################################################
### Definition of the sorted list object class ###
##################################################

class ObjSortedList(ObjList, typename = "SortedList"):
  # Constructor
  def __init__(self, *items):
    ObjList.__init__(self, *items)

  # Insert an item into this list object
  def _py_insert(self):
    insort(self.items, item)
