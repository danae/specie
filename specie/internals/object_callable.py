from .object import Obj, ObjNull, ObjBool
from .errors import InvalidCallException


# Class that defines a callable object
class ObjCallable(Obj):
  # Constructor
  def __init__(self):
    Obj.__init__(self)


  ### Definition of callable functions ###

  # Return the required arguments of the function
  def required_args(self):
    # Return a tuple of type objects
    raise NotImplementedError()

  # Return the required keywords of the function
  def required_kwargs(self):
    # Return a dict of (name, type object) pairs
    raise NotImplementedError()

  # Call the callable
  def call(self, interpreter, args, kwargs):
    raise NotImplementedError()


  ### Definition of conversion functions ###

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}()"

  # Convert to string
  def __str__(self):
    return "<callable>"
