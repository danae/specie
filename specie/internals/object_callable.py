from .object import Obj, ObjNull, ObjBool
from .object_list import ObjList
from .object_record import ObjRecord
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

  # Call the callable, but with internal arguments and keywords
  def call_internal(self, interpreter, *args, **kwargs):
    args = ObjList(args)
    kwargs = ObjRecord.from_dict(kwargs)
    return self.call(interpreter, args, kwargs)


  ### Definition of conversion functions ###

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}()"

  # Convert to string
  def __str__(self):
    return "<callable>"


# Class that defines a native callable object
class ObjNativeCallable(ObjCallable):
  # Initialize a subclass
  def __init_subclass__(cls, /, name, **kwargs):
    super().__init_subclass__(**kwargs)
    cls.name = name

  # Convert to string
  def __str__(self):
    return f"<native callable '{type(self).name}'>"
