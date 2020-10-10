from bisect import insort

from .object import Obj, ObjBool, ObjInt, ObjString
from .object_iterable import ObjIterable, ObjIterator
from .errors import InvalidStateException, InvalidTypeException, UndefinedIndexException


###########################################
### Definition of the list object class ###
###########################################

class ObjList(ObjIterable, typename = "List"):
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

  # Return an iterator for this list object
  def __iter__(self):
    return ObjListIterator(self)

  def method_iterator(self) -> 'ObjIterator':
    return self.__iter__()

  # Return the length of the list object
  def __len__(self):
    return len(self.items)

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Get the item at the specified index in the list object
  def __getitem__(self, index):
    if isinstance(index, (ObjInt, int)):
      index = index.value if isinstance(index, ObjInt) else index
      return self.get_item_at(index)
    raise InvalidTypeException(index)

  def method_at(self, index: 'ObjInt') -> 'Obj':
    return self.__getitem__(index)

  # Add an item to the list object
  def insert(self, item):
    self.items.append(item)

  def method_insert(self, item: 'Obj') -> 'ObjList':
    self.insert(item)
    return self

  # Add several items to the list object
  def insert_all(self, list):
    for item in list:
      self.insert(item)

  def method_insertAll(self, list: 'ObjList') -> 'ObjList':
    self.insert_all(list)
    return self

  # Add an item to the list object and sort it in place
  def insort(self, item):
    insort(self.items, item)

  def method_insort(self, item: 'Obj') -> 'ObjList':
    self.insort(item)
    return self

  # Add several items to the list object and sort them in place
  def insort_all(self, list):
    for item in list:
      self.insort(item)

  def method_insortAll(self, list: 'ObjList') -> 'ObjList':
    self.insort_all(list)
    return self

  # Delete an item from the list object
  def delete(self, item):
    try:
      self.items.remove(item)
    except ValueError:
      pass

  def method_delete(self, item: 'Obj') -> 'ObjList':
    self.delete(item)
    return self

  # Return if the list object contains the specified item
  def __contains__(self, item):
    return item in self.items

  def method_contains(self, item: 'Obj') -> 'ObjBool':
    return ObjBool(self.__contains__(item))


  # Return the Python value for the object
  def _py_value(self):
    return [value._py_value() for value in self.items]

  # Return the Python list for the object
  def _py_list(self):
    return self.items

  # Return the Python representation for the object
  def __repr__(self):
    return f"{self.__class__.__name__}(*{self.items!r})"


  # Convert a Python iterable to a list object
  @classmethod
  def from_py(cls, iterable):
    return cls(*iterable)


####################################################
### Definition of the list iterator object class ###
####################################################

class ObjListIterator(ObjIterator, typename = "ListIterator"):
  # Constructor
  def __init__(self, list):
    super().__init__()

    self.list = list
    self.list_index = None
    self.list_deleted = False


  # Return the element at the cursor of the iterator object
  def current(self):
    if self.list_index is None or self.list_deleted:
      raise InvalidStateException("The iterator has not yet been advanced")
    else:
      return self.list.get_item_at(self.list_index)

  # Advance the cursor of the iterator object
  def advance(self):
    if self.list_index is None:
      self.list_index = 0
    elif self.list_deleted:
      self.list_deleted = False
    else:
      self.list_index += 1
    return self.list_index < len(self.list)

  # Delete the element at the cursor of the iterator object
  def delete(self):
    if self.list_index is None or self.list_deleted:
      raise InvalidStateException("The iterator has not yet been advanced")
    else:
      self.list.delete_item_at(self.list_index)
      self.list_deleted = True
