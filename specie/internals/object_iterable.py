from .object import Obj, ObjNull, ObjBool, ObjInt, ObjString
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

  # Return an iterable with the distinct qelements from this iterable
  def distinct(self):
    return ObjDistinctIterator(iter(self)).delegate()

  def method_distinct(self) -> 'ObjIterable':
    return self.distinct()

  # Return an iterable that only contains items that match the predicate
  def where(self, predicate):
    return ObjWhereIterator(iter(self), predicate).delegate()

  def method_where(self, predicate: 'ObjCallable') -> 'ObjIterable':
    return self.where(predicate)

  # Return the number of elements in this iterable
  def __len__(self):
    return sum(1 for e in iter(self))

  def method_count(self) -> 'ObjInt':
    return ObjInt(self.__len__())

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
    return [e for e in iter(self)]

  def method_asList(self) -> 'ObjList':
    from .object_list import ObjList
    return ObjList(*self.as_list())


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
    return self

  # Return the Python next element for the iterator object
  def __next__(self):
    if self.advance():
      return self.current()
    else:
      raise StopIteration


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

  # Delete the element at the cursor of the iterator object
  def delete(self):
    self.iterator.delete()
