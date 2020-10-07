from bisect import insort

from .object import Obj, ObjBool, ObjInt, ObjString
from .object_traversable import ObjTraversable
from .errors import InvalidTypeException, UndefinedIndexException


###########################################
### Definition of the list object class ###
###########################################

class ObjList(ObjTraversable, typename = "List"):
  # Constructor
  def __init__(self, *items):
    super().__init__()

    self.items = []
    self.insert_all(items)


  # Get an item in the list
  def get_item_at(self, index):
    try:
      return self.items[index]
    except IndexError:
      raise UndefinedIndexException(index)

  # Set an item in the list
  def set_item_at(self, index, value):
    try:
      self.items[index] = value
    except IndexError:
      raise UndefinedIndexException(index)

  # Delete an item from the list
  def delete_item_at(self, index):
    try:
      del self.items[index]
    except IndexError:
      raise UndefinedIndexException(index)


  # Return if the cursor is at a valid position in the traversable object
  def valid(self):
    return self.cursor < len(self.items)

  # Return the element at the cursor of the list object
  def current(self):
    if self.valid():
      return self.items[self.cursor]
    else:
      raise UndefinedIndexException(self.cursor)


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

  # Return the length of this list object
  def __len__(self):
    return len(self.items)

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Get the item at the specified index in this list object
  def __getitem__(self, index):
    if isinstance(index, (ObjInt, int)):
      index = index.value if isinstance(index, ObjInt) else index
      return self.get_item_at(index)
    raise InvalidTypeException(index)

  def method_at(self, index: 'ObjInt') -> 'Obj':
    return self.__getitem__(index)

  # Add an item to this list object
  def insert(self, item):
    self.items.append(item)

  def method_insert(self, item: 'Obj') -> 'ObjList':
    self.insert(item)
    return self

  # Add several items to this list object
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

  # Return if this list object contains the specified item
  def __contains__(self, item):
    return item in self.items

  def method_contains(self, item: 'Obj') -> 'ObjBool':
    return ObjBool(self.__contains__(item))

  # Map the items of the list
  def map(self, func):
    return ObjList.from_py(func(item) for item in self)

  def method_map(self, func: 'ObjCallable') -> 'ObjList':
    return self.map(func)

  # Filter the items of the list
  def where(self, func):
    return ObjList.from_py(item for item in self if func(item))

  def method_where(self, func: 'ObjCallable') -> 'ObjList':
    return self.where(func)


  # Return the Python value for this object
  def _py_value(self):
    return [value._py_value() for value in self.items]

  # Return the Python list for this object
  def _py_list(self):
    return self.items

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}(*{self.items!r})"


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
    super().__init__(*items)

  # Add an item to this list object
  def insert(self, item):
    insort(self.items, item)
