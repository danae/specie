import typing

from .object import Obj, ObjBool, ObjInt, ObjString


###############################################
### Definition of the callable object class ###
###############################################

class ObjCallable(Obj, typename = "Callable"):
  # Constructor
  def __init__(self):
    super().__init__()

  # Return the parameters of the callable
  def parameters(self):
    raise NotImplementedError()

  # Return the result of calling the callable
  def __call__(self, *args):
    raise NotImplementedError()

  def method_call(self, args: 'Obj') -> 'Obj':
    return self.__call__(*args._py_list())

  # Return a callable with the first arguments substituted by the specified arguments
  def partial(self, *args):
    return ObjPartialCallable(self, *args)

  def method_partial(self, args: 'Obj') -> 'ObjCallable':
    return self.partial(*args)


  # Return the string representation of this object
  def __str__(self):
    params = [f"{param}" for param in self.parameters()]
    return f"<{self.__class__.typename}(" + ', '.join(params) + ")>"

  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}()"


#######################################################
### Definition of the partial callable object class ###
#######################################################

class ObjPartialCallable(ObjCallable, typename = "PartialCallable"):
  # Constructor
  def __init__(self, callable, *args):
    super().__init__()
    self.callable = callable
    self.args = args

  # Return the parameters of the callable
  def parameters(self):
    return self.callable.parameters()[len(self.args):]

  # Call the callable
  def __call__(self, *args):
    return self.callable(*self.args, *args)

  # Return the string representation of this object
  def __str__(self):
    params = [' | '.join(p.typename for p in param) if isinstance(param, tuple) else param.typename for param in self.parameters()]
    args = [str(arg) for arg in self.args]
    return f"<{self.__class__.typename}(" + ', '.join(params) + ") bound to (" + ', '.join(args) + ")>"

  def method_string(self) -> 'ObjString':
    return ObjString(self.__str__())


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.callable!r}, *{self.args!r})"


######################################################
### Definition of the Python callable object class ###
######################################################

class ObjPyCallable(ObjCallable, typename = "PyCallable"):
  # Constructor
  def __init__(self, function, *params):
    super().__init__()
    self.function = function
    self.params = params

  # Return the parameters of the callable
  def parameters(self):
    return self.params

  # Return the result of calling the callable
  def __call__(self, *args):
    return self.function(*args)


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.function!r}, *{self.params!r})"
