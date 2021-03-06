from .object import Obj, ObjNull, ObjBool, ObjInt, ObjString
from .object_callable import ObjPyCallable
from .errors import RuntimeException


###############################################
### Definition of the iterable object class ###
###############################################

class ObjIterable(Obj, typename = "Iterable"):
  # Constructor
  def __init__(self):
    super().__init__()


  # Return an iterator for the iterable object
  def __iter__(self):
    raise NotImplementedError()

  def method_iterator(self) -> 'ObjIterator':
    return self.__iter__()


  # Return an iterable with each element of this iterable mapped using the function
  def select(self, function):
    return ObjSelectIterator(iter(self), function).delegate()

  def method_select(self, function: 'ObjCallable') -> 'ObjIterable':
    return self.select(function)

  # Return an iterable with the distinct elements from this iterable
  def distinct(self):
    return ObjDistinctIterator(iter(self)).delegate()

  def method_distinct(self) -> 'ObjIterable':
    return self.distinct()

  # Return an iterable that only contains elements that match the predicate
  def where(self, predicate):
    return ObjWhereIterator(iter(self), predicate).delegate()

  def method_where(self, predicate: 'ObjCallable') -> 'ObjIterable':
    return self.where(predicate)

  # Return an iterable that has its elements sorted using the key function
  def sort(self, key = ObjNull(), desc = ObjBool(False)):
    elements = [e for e in iter(self)]
    elements.sort(key = key if key != ObjNull() else (lambda e: e), reverse = bool(desc))
    return ObjPyIterator(elements).delegate()

  def method_sort(self, key: 'ObjCallable' = ObjNull(), desc: 'ObjBool' = ObjBool(False)) -> 'ObjList':
    return self.sort(key, desc)

  # Return the number of elements in this iterable
  def __len__(self):
    return sum(1 for e in iter(self))

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

  # Fold the elements in this iterable
  def fold(self, function, initial = ObjNull()):
    iterator = iter(self)

    if not isinstance(initial, ObjNull):
      value = initial
    elif iterator.advance():
      value = iterator.current()
    else:
      return initial

    while iterator.advance():
      value = function(value, iterator.current())
    return value

  def method_fold(self, function: 'ObjCallable', initial: 'Obj' = ObjNull()) -> 'Obj':
    return self.fold(function, initial)

  # Return the sum of the elements in this iterable
  def sum(self):
    return self.fold(lambda a, b: a.call_method('add', b))

  def method_sum(self) -> 'Obj':
    return self.sum()

  # Return the minimum of the elements in this iterable
  def min(self):
    return self.fold(lambda a, b: a if bool(a.call_method('lt', b)) else b)

  def method_min(self) -> 'Obj':
    return self.min()

  # Return the maximum of the elements in this iterable
  def max(self):
    return self.fold(lambda a, b: a if bool(a.call_method('gt', b)) else b)

  def method_max(self) -> 'Obj':
    return self.max()

  # Return the average of the elements in this iterable
  def average(self):
    return self.method_sum() / self.method_count()

  def method_average(self) -> 'Obj':
    return self.average()

  # Return if this iterable contains an element
  def __contains__(self, element):
    for e in iter(self):
      if e == element:
        return True
    return False

  def method_contains(self, element: 'Obj') -> 'ObjBool':
    return ObjBool(self.__contains__(element))

  # Return if any element in this iterable matches the predicate
  def any(self, predicate):
    for e in iter(self):
      if predicate(e):
        return True
    return False

  def method_any(self, predicate: 'ObjCallable') -> 'ObjBool':
    return ObjBool(self.any(predicate))

  # Return if all elements in this iterable matches the predicate
  def all(self, predicate):
    for e in iter(self):
      if not predicate(e):
        return False
    return True

  def method_all(self, predicate: 'ObjCallable') -> 'ObjBool':
    return ObjBool(self.all(predicate))

  # Call the function for each element in the iterable and return null
  def each(self, function):
    for e in iter(self):
      function(e)

  def method_each(self, function: 'ObjCallable') -> 'ObjNull':
    self.each(function)
    return ObjNull()

  # Drop all elements in the iterable from the underlying iterator
  def drop(self):
    iterator = iter(self)
    while iterator.advance():
      iterator.delete()

  def method_drop(self) -> 'ObjNull':
    self.drop()
    return ObjNull()

  #Return a list with all elements in the iterable
  def as_list(self):
    from .object_list import ObjList
    return ObjList(*iter(self))

  def method_asList(self) -> 'ObjList':
    return self.as_list()


#########################################################
### Definition of the delegated iterable object class ###
#########################################################

class ObjDelegatedIterable(ObjIterable, typename = "DelegatedIterable"):
  # Constructor
  def __init__(self, iterator):
    super().__init__()

    self.iterator = iterator


  # Return an iterator for the iterable object
  def __iter__(self):
    self.iterator.rewind()
    return self.iterator

  def method_iterator(self) -> 'ObjIterator':
    return self.__iter__()


  # Return the Python representation of this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r})"


###############################################
### Definition of the iterator object class ###
###############################################

class ObjIterator(Obj, typename = "Iterator"):
  # Constructor
  def __init__(self):
    super().__init__()


  # Return the element at the cursor of the iterator object
  def current(self):
    raise NotImplementedError()

  def method_current(self) -> 'Obj':
    return self.current()

  # Advance the cursor of the iterator object
  def advance(self):
    raise NotImplementedError()

  def method_advance(self) -> 'ObjBool':
    return ObjBool(self.advance())

  # Rewind the iterator object
  def rewind(self):
    raise NotImplementedError()

  def method_rewind(self) -> 'ObjNull':
    self.rewind()
    return ObjNull()

  # Delete the element at the cursor of the iterator object
  def delete(self):
    raise RuntimeException(f"{self} does not support deletion")

  def method_delete(self) -> 'ObjNull':
    self.delete()
    return ObjNull()

  # Return an iterable that wraps this iterator
  def delegate(self):
    return ObjDelegatedIterable(self)

  def method_delegate(self) -> 'ObjIterable':
    return self.delegate()


  # Return the Python iterator for the iterator object
  def __iter__(self):
    self.rewind()
    return self

  # Return the Python next element for the iterator object
  def __next__(self):
    if self.advance():
      return self.current()
    else:
      raise StopIteration


######################################################
### Definition of the Python iterator object class ###
######################################################

class ObjPyIterator(ObjIterator, typename = "PyIterator"):
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
      return self.list[self.list_index]

  # Advance the cursor of the iterator object
  def advance(self):
    if self.list_index is None:
      self.list_index = 0
    elif self.list_deleted:
      self.list_deleted = False
    else:
      self.list_index += 1
    return self.list_index < len(self.list)

  # Rewind the iterator object
  def rewind(self):
    self.list_index = None

  # Delete the element at the cursor of the iterator object
  def delete(self):
    if self.list_index is None or self.list_deleted:
      raise InvalidStateException("The iterator has not yet been advanced")
    else:
      del self.list[self.list_index]
      self.list_deleted = True


######################################################
### Definition of the select iterator object class ###
######################################################

class ObjSelectIterator(ObjIterator, typename = "SelectIterator"):
  # Constructor
  def __init__(self, iterator, function):
    super().__init__()

    self.iterator = iterator
    self.function = function


  # Return the element at the cursor of the iterator object
  def current(self):
    return self.function(self.iterator.current())

  # Advance the cursor of the iterator object
  def advance(self):
    return self.iterator.advance()

  # Rewind the iterator object
  def rewind(self):
    self.iterator.rewind()

  # Delete the element at the cursor of the iterator object
  def delete(self):
    self.iterator.delete()


########################################################
### Definition of the distinct iterator object class ###
########################################################

class ObjDistinctIterator(ObjIterator, typename = "DistinctIterator"):
  # Constructor
  def __init__(self, iterator):
    super().__init__()

    self.iterator = iterator
    self.yields = []


  # Return the element at the cursor of the iterator object
  def current(self):
    return self.iterator.current()

  # Advance the cursor of the iterator object
  def advance(self):
    # Advance the iterator until an element matches the predicate
    while self.iterator.advance():
      if (current := self.iterator.current()) not in self.yields:
        self.yields.append(current)
        return True

    # Readed the end of the iterator
    return False

  # Rewind the iterator object
  def rewind(self):
    self.iterator.rewind()

  # Delete the element at the cursor of the iterator object
  def delete(self):
    self.iterator.delete()


#####################################################
### Definition of the where iterator object class ###
#####################################################

class ObjWhereIterator(ObjIterator, typename = "WhereIterator"):
  # Constructor
  def __init__(self, iterator, predicate):
    super().__init__()

    self.iterator = iterator
    self.predicate = predicate


  # Return the element at the cursor of the iterator object
  def current(self):
    return self.iterator.current()

  # Advance the cursor of the iterator object
  def advance(self):
    # Advance the iterator until an element matches the predicate
    while self.iterator.advance():
      if self.predicate(self.iterator.current()):
        return True

    # Readed the end of the iterator
    return False

  # Rewind the iterator object
  def rewind(self):
    self.iterator.rewind()

  # Delete the element at the cursor of the iterator object
  def delete(self):
    self.iterator.delete()
