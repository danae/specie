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
  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(isinstance(other, ObjList) and self.items == other.items)

  # Return the bool representation of this object
  def method_as_bool(self) -> 'ObjBool':
    return ObjBool(bool(self.items))

  # Return the string representation of this object
  def method_as_string(self) -> 'ObjString':
    return ObjString('[' + ', '.join(f"{item}" for item in self.items) + ']')

  # Return the hash of this object
  def method_as_hash(self) -> 'ObjInt':
    return ObjInt(hash(self.value))

  # Return the length of this list object
  def method_count(self) -> 'ObjInt':
    return ObjInt(len(self.items))

  # Return the item in this list object at the specified index
  def method_at(self, index: 'ObjInt') -> 'Obj':
    if isinstance(index, ObjInt):
      try:
        return self.items[index.value]
      except IndexError:
        raise UndefinedIndexException(index)
    raise InvalidTypeException(type(index))

  # Return a slice of this list object
  def method_slice(self, start: 'ObjInt', end: 'ObjInt') -> 'ObjList':
    if isinstance(start, ObjInt):
      if isinstance(end, ObjInt):
        return ObjList(self.items[start.value:end.value])
      raise InvalidTypeException(end)
    raise InvalidTypeException(start)

  # Return if this list object contains the specified item
  def __contains__(self, item):
    return item in self.items

  def method_contains(self, item: 'Obj') -> 'ObjBool':
    return ObjBool(self.__contains__(item))


  # Insert an item into this object
  def insert(self, item: 'Obj') -> 'ObjList':
    self.items.append(item)

  # Insert several items into this list object
  def insert_all(self, iterable) -> 'ObjList':
    for item in iterable:
      self.insert(item)

  # Delete an item from the list
  def delete(self, item: 'Obj') -> 'ObjList':
    self.items.remove(item)

  # Map the items of the list
  def map(self, func: 'ObjCallable') -> 'ObjList':
    return ObjList.from_py(func(item) for item in self)

  # Filter the items of the list
  def filter(self, func: 'ObjCallable') -> 'ObjList':
    return ObjList.from_py(item for item in self if func(item))


  # Return the Python value for this object
  def _py_value(self):
    return [value._py_value() for value in self.items]

  # Return the Python list for this object
  def _py_list(self):
    return self.items

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}(*{self.items!r})"


  # Overload functions for container operators
  def __getitem__(self, index):
    index = ObjInt(index) if isinstance(index, int) else index
    return self.call_method('at', index)

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

  # Insert an item into the list
  def insert(self, item: 'Obj') -> 'ObjList':
    insort(self.items, item)
