from .object import Obj, ObjNull, ObjBool, ObjInt, ObjString


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
### Definition of the delete iterator object class ###
######################################################

class ObjDeleteIterator(ObjIterator, typename = "DeleteIterator"):
  # Constructor
  def __init__(self):
    super().__init__()


  # Delete the element at the cursor of the iterator object
  def delete(self):
    raise NotImplementedError()

  def method_delete(self) -> 'ObjNull':
    self.delete()
    return ObjNull()
