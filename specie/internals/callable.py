from .errors import InvalidCallException


# Class that defines an interface for a callable object
class Callable:
  # Return the signature of the function
  def signature(self):
    raise NotImplementedError()

  # Call the callable
  def call(self, interpreter, arguments, keywords):
    raise NotImplementedError()


# Class that defines a set of callable arguments
class CallableArguments:
  # Constructor
  def __init__(self, args, kwargs):
    self.args = args
    self.kwargs = kwargs

  # Convert to string
  def __str__(self):
    string = ""
    if self.args:
      str += str(self.args)[1:-1]
    if self.kwargs:
      string += (', ' if string else '') + str(self.kwargs)[1:-1]
    return string


# Class that defines a callable signature
class CallableSignature:
  # Constructor
  def __init__(self, args_types, kwargs_types = {}):
    self.args_types = args_types
    self.kwargs_types = kwargs_types
