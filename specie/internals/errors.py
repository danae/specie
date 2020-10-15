# Class that defines a runtime exception
class RuntimeException(Exception):
  def __init__(self, message, location = None):
    self.message = message
    self.location = location

  def __str__(self):
    if self.location is not None:
      return f"{self.message} at {self.location}"
    else:
      return f"{self.message}"


# Exception that is raised when an invalid state is encountered
class InvalidStateException(RuntimeException):
  pass

# Exception that is raised when an invalid operation is encountered
class InvalidOperationException(RuntimeException):
  pass

# Exception that is raised when an invalid type is encountered
class InvalidTypeException(RuntimeException):
  pass

# Exception that is raised when an invalid value is encountered
class InvalidValueException(RuntimeException):
  pass

# Exception that is raised when an invalid call signature is encountered
class InvalidCallException(RuntimeException):
  pass


# Exception that is raised when an undefined method is accessed
class UndefinedMethodException(RuntimeException):
  def __init__(self, method_name, location = None):
    RuntimeException.__init__(self, f"Undefined method '{method_name}'", location)
    self.method_name = method_name

# Exception that is raised when an undefined field is accessed
class UndefinedFieldException(RuntimeException):
  def __init__(self, field_name, location = None):
    RuntimeException.__init__(self, f"Undefined field '{field_name}'", location)
    self.field_name = field_name

# Exception that is raised when an undefined index is accessed
class UndefinedIndexException(RuntimeException):
  def __init__(self, index_name, location = None):
    RuntimeException.__init__(self, f"Undefined index '{index_name}'", location)
    self.index_name = index_name

# Exception that is raised when an undefined index is accessed
class UndefinedKeyException(RuntimeException):
  def __init__(self, index_name, location = None):
    RuntimeException.__init__(self, f"Undefined key '{index_name}'", location)
    self.index_name = index_name
