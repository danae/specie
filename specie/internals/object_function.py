from .object import Obj, ObjBool, ObjInt, ObjString
from .object_callable import ObjCallable


###############################################
### Definition of the function object class ###
###############################################

class ObjFunction(ObjCallable, typename = "Function"):
  # Constructor
  def __init__(self, expr, closure):
    super().__init__()

    self.expr = expr
    self.closure = closure

  # Return the required arguments of the function
  def required_args(self):
    return [Obj] * len(self.expr.parameters)

  # Return the required keywords of the function
  def required_kwargs(self):
    return {}

  # Call the function
  def call(self, interpreter, *args, **kwargs):
    # Create a new environment for this function
    environment = self.closure.nested()

    # Declare the arguments
    for i, parameter in enumerate(self.expr.parameters):
      environment.declare_variable(parameter, args[i])

    # Execute the body and return the result
    return interpreter.evaluate_with(environment, self.expr.body)
