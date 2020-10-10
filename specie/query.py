from . import internals, interpreter, parser


############################################
### Definition of query function classes ###
############################################

# Base class for query functions
class Function:
  # Call the function
  def call(self, interpreter, variable, iterable):
    raise NotImplementedError()

  # Resolve the function
  def resolve(self):
    return []

  # Return the Python representation of this function
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.args!r})"


# Composition of query functions
class Compose(Function):
  # Constructor
  def __init__(self, first, second):
    self.first = first
    self.second = second

  # Call the function
  def call(self, interpreter, variable, iterable):
    return self.second.call(interpreter, variable, self.first.call(interpreter, variable, iterable))

  # Resolve the function
  def resolve(self):
    yield from self.first.resolve()
    yield from self.second.resolve()

  # Return the Python representation of this function
  def __repr__(self):
    return f"{self.__class__.__name__}({self.first!r}, {self.second!r})"


# Select query function
class Select(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function)

  # Resolve the function
  def resolve(self):
    yield self.func


# Distinct query function
class Distinct(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function).method_distinct()

  # Resolve the function
  def resolve(self):
    yield self.func


# Count query function
class Count(Function):
  # Call the function
  def call(self, interpreter, variable, iterable):
    return iterable.method_count()


# Fold query function
class Fold(Function):
  # Constructor
  def __init__(self, func, initial = None):
    self.func = func
    self.initial = initial

  # Call the function
  def call(self, interpreter, variable, iterable):
    function = interpreter.evaluate(self.func)
    if self.initial is not None:
      initial = interpreter.evaluate(self.initial)
      return iterable.method_fold(function, initial)
    else:
      return iterable.method_fold(function)

  # Resolve the function
  def resolve(self):
    yield self.func
    if self.initial is not None:
      yield self.initial


# Sum query function
class Sum(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function).method_sum()

  # Resolve the function
  def resolve(self):
    yield self.func


# Min query function
class Min(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function).method_min()

  # Resolve the function
  def resolve(self):
    yield self.func


# Max query function
class Max(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function).method_max()

  # Resolve the function
  def resolve(self):
    yield self.func


# Average query function
class Average(Function):
  # Constructor
  def __init__(self, func):
    self.func = func

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.func, interpreter.environment)

    return iterable.method_select(function).method_average()

  # Resolve the function
  def resolve(self):
    yield self.func


# Contains query function
class Contains(Function):
  # Constructor
  def __init__(self, element):
    self.element = element

  # Call the function
  def call(self, interpreter, variable, iterable):
    element = interpreter.evaluate(self.element)
    return iterable.method_contains(element)

  # Resolve the function
  def resolve(self):
    yield self.element


# Any query function
class Any(Function):
  # Constructor
  def __init__(self, predicate):
    self.predicate = predicate

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.predicate, interpreter.environment)

    return iterable.method_any(function)

  # Resolve the function
  def resolve(self):
    yield self.predicate


# All query function
class All(Function):
  # Constructor
  def __init__(self, predicate):
    self.predicate = predicate

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.predicate, interpreter.environment)

    return iterable.method_all(function)

  # Resolve the function
  def resolve(self):
    yield self.predicate


# Each query function
class Each(Function):
  # Constructor
  def __init__(self, function):
    self.function = function

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.function, interpreter.environment)
    return iterable.method_each(function)

  # Resolve the function
  def resolve(self):
    yield self.function


# Drop query function
class Drop(Function):
  # Call the function
  def call(self, interpreter, variable, iterable):
    return iterable.method_drop()


# Where query function
class Where(Function):
  # Constructor
  def __init__(self, predicate):
    self.predicate = predicate

  # Call the function
  def call(self, interpreter, variable, iterable):
    function_params = [internals.Parameter(variable, internals.Obj)]
    function = internals.ObjFunction(interpreter, function_params, self.predicate, interpreter.environment)
    return iterable.where(function)

  # Resolve the function
  def resolve(self):
    yield self.predicate


###############################################
### Definition of the query function parser ###
###############################################

def parse_function(name, args):
  # Select query function
  if name.value == "select":
    if len(args) == 1:
      return Select(*args)

  # Distinct query function
  elif name.value == "distinct":
    if len(args) == 1:
      return Distinct(*args)

  # Count query function
  elif name.value == "count":
    if len(args) == 0:
      return Count()

  # Count query function
  elif name.value == "fold":
    if len(args) == 1 or len(args) == 2:
      return Fold(*args)

  # Sum query function
  elif name.value == "sum":
    if len(args) == 1:
      return Sum(*args)

  # Min query function
  elif name.value == "min":
    if len(args) == 1:
      return Min(*args)

  # Max query function
  elif name.value == "max":
    if len(args) == 1:
      return Max(*args)

  # Average query function
  elif name.value == "average":
    if len(args) == 1:
      return Average(*args)

  # Contains query function
  elif name.value == "contains":
    if len(args) == 1:
      return Contains(*args)

  # Any query function
  elif name.value == "any":
    if len(args) == 1:
      return Any(*args)

  # All query function
  elif name.value == "all":
    if len(args) == 1:
      return All(*args)

  # Each query function
  elif name.value == "each":
    if len(args) == 1:
      return Each(*args)

  # Drop query function
  elif name.value == "drop":
    if len(args) == 0:
      return Drop()

  # Where query function
  elif name.value == "where":
    if len(args) == 1:
      return Where(*args)

  # Undefined query functon, so raise a parser error
  raise parser.ParserError(f"Invalid query function {name.value}", name.location)
