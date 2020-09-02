from bisect import insort

from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjInt
from .errors import InvalidTypeException, UndefinedIndex


# Class that defines a collection object
class ObjCollection(Obj):
  # Constructor
  def __init__(self, iterable = []):
    Obj.__init__(self)

    self.items = []
    self.insert_all(iterable)

    self.set_method('at', self.__getitem__)
    self.set_method('count', self.count)
    self.set_method('contains', self.__contains__)

  # Return the truthyness of this object
  def truthy(self):
    return ObjBool(bool(self.items))

  # Return if this collection object is equal to another object
  def __eq__(self, other):
    return ObjBool(isinstance(other, ObjCollection) and self.items == other.items)

  # Return the item in the collection at the specified index
  def __getitem__(self, index):
    if isinstance(index, ObjInt):
      try:
        return self.items[index.value]
      except IndexError:
        raise UndefinedIndex(index)
    else:
      raise InvalidTypeException(index)

  # Return the length of the collection
  def count(self):
    return ObjInt(len(self.items))

  # Return if the specified item exists in the collection
  def __contains__(self, item):
    return ObjBool(item in self.items)

  # Insert an item into the collection
  def insert(self, item):
    if isinstance(item, Obj):
      self.items.append(item)
    else:
      raise InvalidTypeException(item)

  # Add several items to the collection
  def insert_all(self, iterable):
    for item in iterable:
      self.insert(item)

  # Delete an item from the collection
  def delete(self, item):
    self.items.remove(item)

  # Map the items of the collection
  def map(self, func):
    return ObjCollection(func(item) for item in self)

  # Filter the items of the collection
  def filter(self, func):
    return ObjCollection(item for item in self if func(item))

  # Convert to hash
  def __hash__(self):
    return hash((self.items))

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


# Class that defines a sorted collection object
class ObjSortedCollection(ObjCollection):
  # Constructor
  def __init__(self, iterable = []):
    ObjCollection.__init__(self, iterable)

  # Insert an item into the collection
  def insert(self, item):
    if isinstance(item, Obj):
      insort(self.items, item)
    else:
      raise InvalidTypeException(item)
