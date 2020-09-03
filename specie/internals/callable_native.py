import inspect

from .callable import Callable
from .object import Obj, ObjNull, ObjBool
from .object_numeric import ObjNumeric, ObjFloat
from .object_collection import ObjCollection
from .errors import InvalidTypeException, UndefinedMethod


# Class that defines a callable that calls a native function
class NativeFunction(Callable):
  # Constructor
  def __init__(self, function):
    self.function = function

  # Return the arity of the function
  def arity(self):
    signature = inspect.signature(self.function)
    return len([p for p in signature.parameters.values() if p.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]])

  # Call the function
  def call(self, interpreter, arguments):
    return self.function(*arguments)


# Class that defines a call to a method
class MethodFunction(Callable):
  # Constructor
  def __init__(self, method, method_arity):
    self.method = method
    self.method_arity = method_arity

  # Return the arity of the callable
  def arity(self):
    return self.method_arity

  # Call the function
  def call(self, interpreter, arguments):
    if isinstance(arguments[0], Obj):
      return arguments[0].call(self.method, *arguments[1:])
    else:
      raise InvalidTypeException(arguments[0])


# Class that defines a call to two reflective methods
class ReflectiveMethodFunction(Callable):
  # Constructor
  def __init__(self, l_method, r_method):
    self.l_method = l_method
    self.r_method = r_method

  # Return the arity of the callable
  def arity(self):
    return 2

  # Call the function
  def call(self, interpreter, arguments):
    l_obj, r_obj = arguments
    if l_obj.has_method(self.l_method):
      return l_obj.call(self.l_method, r_obj)
    elif r_obj.has_method(self.r_method):
      return r_obj.call(self.r_method, l_obj)
    else:
      raise UndefinedMethod([self.l_method, self.r_method])


# Class that defines the sum function
class SumFunction(Callable):
  # Return the arity of the callable
  def arity(self):
    return 1

  # Return the result of a call to the callable
  def call(self, interpreter, arguments):
    if not isinstance(arguments[0], ObjCollection):
      raise InvalidTypeException(f"sum() requires a collection as its frst argument, {type(arguments[0])} given")

    # Calculate the sum of the list items
    sum = ObjFloat()
    for item in arguments[0]:
      if not isinstance(item, ObjNumeric):
        raise InvalidTypeException(f"sum() requires each list item to be numeric, {type(item)} given")
      sum += item

    # Return the sum
    return sum


# Class that defines the avg function
class AvgFunction(Callable):
  # Return the arity of the callable
  def arity(self):
    return 1

  # Return the result of a call to the callable
  def call(self, interpreter, arguments):
    if not isinstance(arguments[0], ObjCollection):
      raise InvalidTypeException(f"sum() requires a collection as its frst argument, {type(arguments[0])} given")

    # Calculate the sum of the list items
    sum = ObjFloat()
    for item in arguments[0]:
      if not isinstance(item, ObjNumeric):
        raise InvalidTypeException(f"sum() requires each list item to be numeric, {type(item)} given")
      sum += item

    # Return the average
    return sum / arguments[0].call('count')
