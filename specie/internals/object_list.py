from bisect import insort

from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjInt
from .errors import InvalidTypeException, UndefinedIndexException


# Class that defines a list object
class ObjList(Obj):
  # Constructor
  def __init__(self, iterable = []):
    Obj.__init__(self)

    self.items = []
    self.insert_all(iterable)

    self.set_method('at', self.__getitem__)
    self.set_method('count', self.count)
    self.set_method('contains', self.__contains__)


  ### Definition of object functions ###

  # Return the primitive value of this object
  def value(self):
    return [value.value() for value in self.items]

  # Return the truthyness of this object
  def truthy(self):
    return ObjBool(bool(self.items))

  # Return if this list object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjList) and self.items == other.items)

  # Return the item in the list at the specified index
  def __getitem__(self, index):
    if isinstance(index, ObjInt):
      try:
        return self.items[index.value()]
      except IndexError:
        raise UndefinedIndexException(index)
    elif isinstance(index, int):
      return self.items[index]
    else:
      raise InvalidTypeException(type(index))

  # Return the length of the list
  def count(self):
    return ObjInt(len(self.items))

  # Return if the specified item exists in the list
  def __contains__(self, item):
    return ObjBool(item in self.items)

  # Insert an item into the list
  def insert(self, item):
    if isinstance(item, Obj):
      self.items.append(item)
    else:
      raise InvalidTypeException(item)

  # Add several items to the list
  def insert_all(self, iterable):
    for item in iterable:
      self.insert(item)

  # Delete an item from the list
  def delete(self, item):
    self.items.remove(item)

  # Map the items of the list
  def map(self, func):
    return ObjList(func(item) for item in self)

  # Filter the items of the list
  def filter(self, func):
    return ObjList(item for item in self if func(item))


  ### Definition of conversion functions

  # Convert to iterator
  def __iter__(self):
    return iter(self.items)

  # Cnvert to length
  def __len__(self):
    return int(self.count())

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.items!r})"

  # Convert to string
  def __str__(self):
    return '[' + ', '.join(f"{item}" for item in self.items) + ']'


# Class that defines a sorted list object
class ObjSortedList(ObjList):
  # Constructor
  def __init__(self, iterable = []):
    ObjList.__init__(self, iterable)

  # Insert an item into the list
  def insert(self, item):
    if isinstance(item, Obj):
      insort(self.items, item)
    else:
      raise InvalidTypeException(item)
