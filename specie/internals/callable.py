# Class that defines an interface for a callable object
class Callable:
  # Return the arity (number of arguments) of the callable
  def arity(self):
    raise NotImplementedException()

  # Return the result of a call to the callable
  def call(self, interpreter, arguments):
    raise NotImplementedException()
