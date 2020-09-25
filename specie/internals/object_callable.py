from .object import Obj, ObjBool, ObjInt, ObjString


###############################################
### Definition of the callable object class ###
###############################################

class ObjCallable(Obj, typename = "Callable"):
  # Constructor
  def __init__(self):
    Obj.__init__(self)

  # Return the required arguments of the callable as a tuple
  def required_args(self):
    raise NotImplementedError()

  # Return the required keywords of the callable as a dict
  def required_kwargs(self):
    raise NotImplementedError()

  # Return the result of calling the callable
  def __call__(self, *args, **kwargs):
    raise NotImplementedError()

  def method_call(self, args: 'Obj', kwargs: 'Obj') -> 'Obj':
    return self(*args._py_list(), **kwargs._py_dict())

  # Return a callable with its first argument bound to an object
  def bind(self, this_arg):
    return ObjBoundCallable(self, this_arg)

  def method_bind(self, this_arg: 'Obj') -> 'ObjCallable':
    return self.bind(this_arg)


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}()"


#####################################################
### Definition of the bound callable object class ###
#####################################################

class ObjBoundCallable(ObjCallable, typename = "BoundCallable"):
  # Constructor
  def __init__(self, callable, this_arg):
    ObjCallable.__init__(self)

    self.callable = callable
    self.this_arg = this_arg

  # Return the required arguments of the function
  def required_args(self):
    return self.callable.required_args()[1:]

  # Return the required keywords of the function
  def required_kwargs(self):
    return self.callable.required_kwargs()

  # Call the callable
  def __call__(self, *args, **kwargs):
    return self.callable(self.this_arg, *args, **kwargs)

  # Return the string representation of this object
  def __str__(self):
    return f"<{self.__class__.typename}: bound to {self.this_arg}>"

  def method_string(self) -> 'ObjString':
    return ObjString(self.__str__())


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.callable!r}, {self.this_arg!r})"


######################################################
### Definition of the native callable object class ###
######################################################

class ObjNativeCallable(ObjCallable, typename = "NativeCallable"):
  # Constructor
  def __init__(self, function, required_args, required_kwargs):
    ObjCallable.__init__(self)

    self.function = function
    self._required_args = required_args
    self._required_kwargs = required_kwargs

  # Return the required arguments of the callable as a tuple
  def required_args(self):
    return self._required_args

  # Return the required keywords of the callable as a dict
  def required_kwargs(self):
    return self._required_kwargs

  # Return the result of calling the callable
  def __call__(self, *args, **kwargs):
    return self.function(*args, **kwargs)


  # Return the Python representation for this object
  def __repr__(self):
    return f"{self.__class__.__name__}({self.function!r}, {self._required_args!r}, {self._required_kwargs!r})"
