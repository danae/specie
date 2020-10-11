import inspect
import math

from .errors import InvalidCallException


######################################
### Definition of parameter helper ###
######################################

# Singleton class that defines when a parameter is required
class ParameterRequired:
  pass

# Singleton class that defines when a parameter is variadic
class ParameterVariadic:
  pass


#########################################
### Definition of the parameter class ###
#########################################

class Parameter:
  # Constructor
  def __init__(self, name, type, default = ParameterRequired):
    self.name = name
    self.type = type
    self.default = default

  # Return if this parameter is optional
  def is_optional(self):
    return self.default is not ParameterRequired and self.default is not ParameterVariadic

  # Return if this parameter is variadic
  def is_variadic(self):
    return self.default is ParameterVariadic

  # Return the string representation for this parameter
  def __str__(self):
    if self.default is ParameterVariadic:
      return f"...{self.name}"
    elif self.default is ParameterRequired:
      return f"{self.name}"
    else:
      return f"{self.name} = {self.default}"

  # Return the Python representation for this parameter
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.type!r}, {self.default!r})"


##############################################
### Definition of the parameter list class ###
##############################################

class Parameters:
  # Constructor
  def __init__(self, *parameters):
    self.parameters = list(parameters)

  # Return an iterator for this parameter list
  def __iter__(self):
    return iter(self.parameters)

  # Return the length of this parameter list
  def __len__(self):
    return len(self.parameters)

  # Return an item from this parameter list
  def __getitem__(self, index):
    if isinstance(index, slice):
      return Parameters(*self.parameters[index])
    else:
      return self.parameters[index]

  # Return if this parameter list has optional parameters
  def has_optional(self):
    return any(param.is_optional() for param in self.parameters)

  # Return if this parameter list has variadic parameters
  def has_variadic(self):
    return any(param.is_variadic() for param in self.parameters)

  # Return the minimul length of an argument list
  def min_length(self):
    if self.has_variadic():
      return len([param for param in self.parameters if not param.is_variadic()])
    elif self.has_optional():
      return len([param for param in self.parameters if not param.is_optional()])
    else:
      return len(self.parameters)

  # Return the minimal length of an argument list
  def max_length(self):
    if self.has_variadic():
      return math.inf
    else:
      return len(self.parameters)

  # Return a string representation of the length range
  def format_length(self):
    min_length = self.min_length()
    max_length = self.max_length()

    if min_length == max_length:
      return f"{min_length}"
    elif max_length == math.inf:
      return f"{min_length} or more"
    else:
      return f"between {min_length} and {max_length}"

  # Validate an argument list against this parameter list and map it to a proper list
  def validate(self, args, location = None):
    from .object_list import ObjList

    # Check the length of the arguments
    args_length = len(args)
    if args_length < self.min_length() or args_length > self.max_length():
      raise InvalidCallException(f"Expected {self.format_length()} arguments, got {args_length}", location)

    # Create a list to store the mapped arguments
    args_list = []

    # Iterate over the parameters
    for i, param in enumerate(self.parameters):
      # Check if an argument for this parameter exists
      if i < len(args):
        # Yes, so go get the argument
        arg = args[i]

        # Check the type of the argument
        if not issubclass(check_type := type(arg), param_type := param.type):
          raise InvalidCallException(f"Expected argument '{param.name}' of type {param_type.typename}, got type {check_type.typename}", location)

        # Add the argument to the list
        if i == len(self.parameters) - 1 and param.is_variadic():
          args_list.append(ObjList(arg))
        else:
          args_list.append(arg)
      else:
        # No, so this should be a optional or variadic parameter
        if i == len(self.parameters) - 1 and param.is_variadic():
          args_list.append(ObjList())
        else:
          args_list.append(param.default)

    # Check if there are arguments left
    if self.has_variadic() and len(self.parameters) < len(args):
      # Add the remaining arguments to the last variadic argument
      for i in range(len(self.parameters), len(args)):
        args_list[-1].insert(args[i])

    # Return the list as a list object
    return ObjList(*args_list)

  # Return the string representation for this parameter
  def __str__(self):
    return ", ".join(f"{param}" for param in self.parameters)

  # Return the Python representation for this parameter
  def __repr__(self):
    return f"{self.__class__.__name__}(*{self.parameters!r})"

  # Return a parameter list from a callable
  @classmethod
  def from_callable(cls, callable, self_type = None):
    # Create a list to store the parameters
    params = []

    # Iterate over the callablesignature
    signature = inspect.signature(callable)
    for param in signature.parameters.values():
      # Check the parameter kind
      if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
        # Required or optional parameter
        default = param.default if param.default is not param.empty else ParameterRequired
        params.append(Parameter(param.name, cls.resolve_type(param, self_type), default))
      elif param.kind == param.VAR_POSITIONAL:
        # Variadic parameter
        if not any(param.is_variadic() for param in params):
          params.append(Parameter(param.name, cls.resolve_type(param, self_type), ParameterVariadic))
        else:
          raise RuntimeError(f"Disallowed second variadic parameter {param} in callable {callable}")
      else:
        # Probably keywords
        raise RuntimeError(f"Disallowed keyword parameter {param} in callable {callable}")

    # Return the list as a parameter list
    return cls(*params)

  # Return a parameter resolved to a class
  @classmethod
  def resolve_type(cls, param, self_type = None):
    from .object import ObjMeta

    if param.name == "self" and self_type is not None:
      return self_type
    elif param.annotation == param.empty:
      return ObjMeta.obj_classes['Obj']
    elif ',' not in param.annotation:
      return ObjMeta.obj_classes[param.annotation]
    else:
      return tuple(ObjMeta.obj_classes[annot.strip()] for annot in param.annotation.split(','))
