# Class that defines a runtime exception
class RuntimeException(Exception):
  def __init__(self, message):
    self.message = message


# Exception that is raised when an invalid type is encountered
class InvalidTypeException(RuntimeException):
  def __init__(self, message):
    self.message = message


# Exception that is raised when an invalid value is encountered
class InvalidValueException(RuntimeException):
  def __init__(self, message):
    self.message = message


# Exception that is raised when an undefined method is accessed
class UndefinedMethod(RuntimeException):
  def __init__(self, method_name):
    self.method_name = method_name
    self.message = f"Undefined method '{method_name}'"


# Exception that is raised when an undefined field is accessed
class UndefinedField(RuntimeException):
  def __init__(self, field_name):
    self.field_name = field_name
    self.message = f"Undefined field '{field_name}'"


# Exception that is raised when an undefined index is accessed
class UndefinedIndex(RuntimeException):
  def __init__(self, index_name):
    self.index_name = index_name
    self.message = f"Undefined index '{index_name}'"
