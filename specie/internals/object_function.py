from .object import Obj, ObjBool, ObjInt, ObjString
from .object_callable import ObjCallable


###############################################
### Definition of the function object class ###
###############################################

class ObjFunction(ObjCallable, typename = "Function"):
  # Constructor
  def __init__(self, interpreter, params, body, closure):
    super().__init__()
    self.interpreter = interpreter
    self.params = params
    self.body = body
    self.closure = closure

  # Return the parameters of the callable
  def parameters(self):
    return self.params

  # Call the function
  def __call__(self, *args):
    # Create a new environment for this function
    environment = self.closure.nested()

    # Declare the arguments
    for param, arg in zip(self.params, args):
      environment.declare(param.name, arg)

    # Execute the body and return the result
    return self.interpreter.evaluate_with(environment, self.body)
