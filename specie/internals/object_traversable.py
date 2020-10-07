from .object import Obj, ObjBool, ObjInt, ObjString


##################################################
### Definition of the traversable object class ###
##################################################

class ObjTraversable(Obj, typename = "Traversable"):
  # Constructor
  def __init__(self):
    super().__init__()

    self.cursor = 0


  # Return if the cursor is at a valid position in the traversable object
  def valid(self):
    raise NotImplementedError()

  def method_valid(self) -> 'ObjBool':
    return ObjBool(self.valid())

  # Return the element at the cursor of the traversable object
  def current(self):
    raise NotImplementedError()

  def method_current(self) -> 'Obj':
    return self.current()

  # Return the cursor of the traversable object
  def pos(self):
    return self.cursor

  def method_pos(self) -> 'ObjInt':
    return ObjInt(self.pos())

  # Advance the cursor of the traversable object
  def advance(self):
    self.cursor += 1
    return self.valid()

  def method_advance(self) -> 'ObjBool':
    return ObjBool(self.advance())

  # Rewind the cursor of the traversable object
  def rewind(self):
    self.cursor = 0
    return self.valid()

  def method_rewind(self) -> 'ObjBool':
    return ObjBool(self.rewind())


  # Return the Python iterator for the traversable object
  def __iter__(self):
    self.rewind()
    while self.valid():
      yield self.current()
      self.advance()
