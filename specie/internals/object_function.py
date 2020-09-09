from .object import Obj, ObjNull, ObjBool
from .object_callable import ObjCallable


# Class that defines a function object
class ObjFunction(ObjCallable):
  # Constructor
  def __init__(self, expr):
    ObjCallable.__init__(self)
    self.expr = expr


  ### Definition of callable functions ###

  # Return the required arguments of the function
  def required_args(self):
    return [Obj] * len(self.expr.parameters)

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, args, kwargs):
    # Begin a new scope for this function
    interpreter.begin_scope()

    # Declare the arguments
    for i, parameter in enumerate(self.expr.parameters):
      interpreter.environment.declare_variable(parameter, args[i])

    # Execute the body
    result = interpreter.evaluate(self.expr.body)

    # End the function scope
    interpreter.end_scope()

    # Return the result
    return result


  ## Definition of conversion functions

  # Convert to string
  def __str__(self):
    return f"<function: {self.expr}>"
