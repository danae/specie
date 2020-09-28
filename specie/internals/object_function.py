from .object import Obj, ObjBool, ObjInt, ObjString
from .object_callable import ObjCallable


###############################################
### Definition of the function object class ###
###############################################

class ObjFunction(ObjCallable, typename = "Function"):
  # Constructor
  def __init__(self, interpreter, expr, closure):
    super().__init__()
    self.interpreter = interpreter
    self.expr = expr
    self.closure = closure

  # Return the parameters of the callable
  def parameters(self):
    return [Obj] * len(self.expr.parameters)

  # Call the function
  def __call__(self, *args, **kwargs):
    # Create a new environment for this function
    environment = self.closure.nested()

    # Declare the arguments
    for i, parameter in enumerate(self.expr.parameters):
      environment.declare_variable(parameter, args[i])

    # Execute the body and return the result
    return self.interpreter.evaluate_with(environment, self.expr.body)
