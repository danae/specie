import os.path

from colorama import Fore, Back, Style

from . import ast, grammar, internals, output, parser, query, semantics


#####################################
### Definition of the environment ###
#####################################

# Class that defines an environment
class Environment:
  # Constructor
  def __init__(self, previous = None, variables = None):
    self.previous = previous
    self.variables = variables or internals.ObjRecord()

  # Get a variable in the environment
  def __getitem__(self, name):
    # Get a variable from the current environment
    if self.variables.has_field(name):
      return self.variables.get_field(name)

    # Get a variable from the previous environment
    elif self.previous is not None:
      return self.previous[name]

    # No matching variable found
    else:
      raise IndexError(f"Undefined field '{name}'")

  # Set a variable in the environment
  def __setitem__(self, name, value):
    # Set a variable in the current environment
    if self.variables.has_field(name):
      self.variables.set_field(name, value)

    # Get a variable from the previous environment
    elif self.previous is not None:
      self.previous[name] = value

    # No matching variable found
    else:
      raise KeyError(f"Undefined field '{name}'")

  # Return is a variable exists in the environment
  def __contains__(self, name):
    # Check the current environment
    if self.variables.has_field():
      return True

    # Check the previous environment
    elif self.previous is not None:
      return name in self.previous

    # No matching variable found
    else:
      return False

  # Set a varable in the CURRENT environmentn
  def declare(self, name, value):
    self.variables.declare_field(name, value)

  # Create a nested environment with this environment as previous environment
  def nested(self):
    return Environment(self)

  # Return the ancestor of this environment at the specified distance
  def ancestor(self, distance):
    environment = self
    for _ in range(distance):
      environment = environment.previous
    return environment

  # Get a variable in the environment by means of a lexer token
  def get_variable(self, name, distance = 0):
    try:
      if distance == 0:
        return self.variables.get_field(name.value, name.location)
      else:
        return self.ancestor(distance).variables.get_field(name.value, name.location)
    except KeyError:
      raise internals.UndefinedFieldException(f"{name.value}", name.location)

  # Set a variable in the environment by means of a lexer token
  def set_variable(self, name, value, distance = 0):
    try:
      if distance == 0:
        self.variables.set_field(name.value, value, name.location)
      else:
        self.ancestor(distance).variables.set_field(name.value, value, name.location)
    except KeyError:
      raise internals.UndefinedFieldException(name.value, name.location)

  # Return if the environment contains the specified variable
  def has_variable(self, name, distance = 0):
    if distance == 0:
      return self.variables.has_field(name.value)
    else:
      return self.ancestor(distance).variables.has_field(name.value)

  # Declare a varable in the CURRENT environment by means of a lexer token
  def declare_variable(self, name, value, **kwargs):
    self.variables.declare_field(name.value, value, **kwargs)

  # Return an iterator over this environment and its ancestors
  def __iter__(self):
    yield self
    if self.previous is not None:
      yield from self.previous

  # Convert to string
  def __str__(self):
    string = '(' + ', '.join(self.variables.names()) + ')'
    if self.previous is not None:
      string += " -> " + str(self.previous)
    return string

  # Return a global environment
  @classmethod
  def globals(cls, interpreter):
    globals = internals.ObjRecord()

    # Types
    globals.declare_field('bool', internals.ObjPyCallable(internals.ObjBool), mutable = False)
    globals.declare_field('int', internals.ObjPyCallable(internals.ObjInt), mutable = False)
    globals.declare_field('float', internals.ObjPyCallable(internals.ObjFloat), mutable = False)
    globals.declare_field('string', internals.ObjPyCallable(internals.ObjString), mutable = False)
    globals.declare_field('map', internals.ObjPyCallable(internals.ObjMap), mutable = False)
    globals.declare_field('date', internals.ObjPyCallable(internals.ObjDate), mutable = False)
    globals.declare_field('money', internals.ObjPyCallable(internals.ObjMoney), mutable = False)

    # Global functions
    globals.declare_field('print', internals.ObjPyCallable(output.print_object), mutable = False)
    globals.declare_field('printTitle', internals.ObjPyCallable(output.title), mutable = False)
    globals.declare_field('include', internals.ObjPyCallable(interpreter.include), mutable = False)

    # Namespaces
    globals.declare_field('import', internals.namespace_import(interpreter), mutable = False)

    # Tables
    globals.declare_field('_', internals.ObjList())

    return cls(None, globals)


#####################################
### Definition of the interpreter ###
#####################################

# Class that defines an interpreter
class Interpreter(ast.ExprVisitor[internals.Obj]):
  # Constructor
  def __init__(self):
    # Define the environment
    self.globals = Environment.globals(self)
    self.environment = self.globals

    # Define the include stack; the first file is the interactive console
    self.includes = [None]

    # Define the map of local variables
    self.locals = {}

    # Define the static analyzers
    self.resolver = semantics.Resolver(self)

  # Parse a string into an abstract syntax tree and interpret it
  def execute(self, string, is_module = True):
    # Check if the string is empty
    if not string.strip():
      return

    # Parse and interpret the string
    try:
      # Parse the string into an abstract syntax tree
      ast = grammar.parse(string, is_module)

      # Semantically analyse the tree
      self.resolver.resolve(ast)

      # Interpret the abstract syntax tree
      result = self.evaluate(ast)
      if not self.includes[-1] and result != internals.ObjNull():
        output.print_object(result)

      # Return the result
      return result

    # Catch syntax errors
    except parser.SyntaxError as err:
      print(f"{Style.BRIGHT}{Fore.RED}{err}{Style.RESET_ALL}")
      print(err.location.point(string, 2))

    # Catch unexpected token errors
    except parser.ParserError as err:
      print(f"{Style.BRIGHT}{Fore.RED}{err}{Style.RESET_ALL}")
      if err.location:
        print(err.location.point(string, 2))

    # Catch runtime errors
    except internals.RuntimeException as err:
      print(f"{Style.BRIGHT}{Fore.RED}{err.__class__.__name__}: {err}{Style.RESET_ALL}")
      if err.location:
        print(err.location.point(string, 2))


  # Resolve a file name
  def resolve_file_name(self, file_name):
    # If it's an absolute path, just check if it exists
    if os.path.isfile(file_name):
      return file_name

    # If an include file is defined, check relative to that
    if (include := self.includes[-1]) and os.path.exists(include):
      include_file_name = os.path.join(os.path.dirname(include), file_name)
      if os.path.isfile(include_file_name):
        return include_file_name

    # No matching file name found
    return None


  # Include a file
  def include(self, file_name: 'ObjString'):
    file_name = file_name.value if isinstance(file_name, internals.ObjString) else file_name

    # Check if the file exists
    if (resolved_file_name := self.resolve_file_name(file_name)) is None:
      raise internals.RuntimeException(f"Include failed: the file '{file_name}' could not be found")

    # Add the file to the include stack
    self.includes.append(resolved_file_name)

    # Open the file and execute the contents
    with open(resolved_file_name, 'r') as file:
      string = file.read()
      result = self.execute(string)

    # Remove the file from the include stack
    self.includes.pop()

    # Return the result
    return result


  # Evaluate an expression
  def evaluate(self, expr: ast.Expr) -> internals.Obj:
    return expr.accept(self)

  # Evaluate an expression with the given environment
  def evaluate_with(self, environment: Environment, *exprs: ast.Expr) -> internals.Obj:
    # Set the new environment
    previous = self.environment
    self.environment = environment

    # Evaluate the expressions
    result = None
    for expr in exprs:
      result = self.evaluate(expr)

    # Reset the environment
    self.environment = previous

    # Return the result
    return result

  # Visit a literal expression
  def visit_literal_expr(self, expr: ast.LiteralExpr) -> internals.Obj:
    return expr.object

  # Visit a list expression
  def visit_list_expr(self, expr: ast.ListExpr) -> internals.Obj:
    list_object = internals.ObjList()
    for item in expr:
      list_object.insert(self.evaluate(item))
    return list_object

  # Visit a record expression
  def visit_record_expr(self, expr: ast.RecordExpr) -> internals.Obj:
    record_object = internals.ObjRecord()
    for name, value in expr:
      record_object.declare_field(name.value, self.evaluate(value), name.location)
    return record_object

  # Visit a variable expression
  def visit_variable_expr(self, expr: ast.VariableExpr) -> internals.Obj:
    # Get the distance of the local variable, or otherwise assume it's global
    distance = self.locals.get(expr)
    if distance is not None:
      # Get a local variable
      return self.environment.get_variable(expr.name, distance)
    else:
      # Get a global variable
      return self.globals.get_variable(expr.name)

  # Visit a grouping expression
  def visit_grouping_expr(self, expr: ast.GroupingExpr) -> internals.Obj:
    return self.evaluate(expr.expression)

  # Visit a call expression
  def visit_call_expr(self, expr: ast.CallExpr) -> internals.Obj:
    # Evaluate the expression
    callable = self.evaluate(expr.expression)

    # Check if the expression is callable
    if not isinstance(callable, internals.ObjCallable):
      raise internals.RuntimeException(f"The expression '{expr.expression}' is not callable", expr.token.location)

    # Evaluate the arguments and validate them
    args = self.evaluate(expr.args)
    args = callable.parameters().validate(args)

    # Call the callable
    return callable(*args)

  # Visit a get expression
  def visit_get_expr(self, expr: ast.GetExpr) -> internals.Obj:
    # Evaluate the expression
    expression = self.evaluate(expr.expression)

    # Return the field of the record
    if isinstance(expression, internals.ObjRecord):
      if expression.has_field(expr.name.value):
        return expression.get_field(expr.name.value)

    # Return the method of the object
    if expression.has_method(expr.name.value):
      return expression.get_method(expr.name.value)

    # Nothing found to get
    raise internals.RuntimeException(f"The expression '{expr.expression}' is either not a record or the specified field or method is undefined", expr.token.location)

  # Visit a set expression
  def visit_set_expr(self, expr: ast.GetExpr) -> internals.Obj:
    # Evaluate the expression
    expression = self.evaluate(expr.expression)

    # Check if the object is a record
    if not isinstance(expression, internals.ObjRecord):
      raise internals.RuntimeException(f"The expression '{expr.expression}' is not a record", expr.token.location)

    # Evaluate the value
    value = self.evaluate(expr.value)

    # Set the field of the record
    expression.set_field(expr.name.value, value)

    # Return the value
    return value

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr: ast.UnaryOpExpr) -> internals.Obj:
    op = expr.op.value

    # Logic operations
    if op == 'not':
      return internals.ObjBool(not bool(self.evaluate(expr.expression)))

    # No matching operation found
    raise internals.RuntimeException("Undefined unary operator '{}'".format(op), expr.op.location)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr: ast.BinaryOpExpr) -> internals.Obj:
    op = expr.op.value

    # Evaluate the operands
    left = self.evaluate(expr.left)
    right = self.evaluate(expr.right)

    # Arithmetic operations
    if op == '*':
      return left.call_method('mul', right)
    elif op == '/':
      return left.call_method('div', right)
    elif op == '+':
      return left.call_method('add', right)
    elif op == '-':
      return left.call_method('sub', right)

    # Comparison operations
    elif op == '<':
      return left.call_method('lt', right).method_asBool()
    elif op == '<=':
      return left.call_method('lte', right).method_asBool()
    elif op == '>':
      return left.call_method('gt', right).method_asBool()
    elif op == '>=':
      return left.call_method('gte', right).method_asBool()
    elif op == '<=>':
      return left.call_method('cmp', right).method_asBool()
    elif op == '=~':
      return left.call_method('match', right).method_asBool()
    elif op == '!~':
      return left.call_method('match', right).method_asBool().negate()
    
    # Containment operations
    elif op == 'in':
      return right.call_method('contains', left).method_asBool()
    elif op == '!in':
      return right.call_method('contains', left).method_asBool().negate()
    
    # Equality operations
    elif op == '==':
      return left.call_method('eq', right).method_asBool()
    elif op == '!=':
      return left.call_method('eq', right).method_asBool().negate()

    # No matching operation found
    raise internals.RuntimeException("Undefined binary operator '{}'".format(op), expr.op.location)

  # Visit a logical expression
  def visit_logical_expr(self, expr: ast.LogicalExpr) -> internals.Obj:
    op = expr.op.value

    # Logical and
    if op == 'and':
      return internals.ObjBool(self.evaluate(expr.left)) and internals.ObjBool(self.evaluate(expr.right))

    # Logical or
    elif op == 'or':
      return internals.ObjBool(self.evaluate(expr.left)) or internals.ObjBool(self.evaluate(expr.right))

    # No matching operation found
    raise internals.RuntimeException("Undefined binary operator '{}'".format(op), expr.op.location)

  # Visit an if expression
  def visit_if_expr(self, expr: ast.IfExpr) -> internals.Obj:
    # Evaluate the condition
    condition = bool(self.evaluate(expr.condition))
    if condition:
      # Evaluate the then clause
      return self.evaluate(expr.then_clause)
    elif expr.else_clause is not None:
      # Evaluate the else clause if present, else return null
      return self.evaluate(expr.else_clause)
    else:
      return internals.ObjNull()

  # Visit a for expression
  def visit_for_expr(self, expr: ast.ForExpr) -> internals.Obj:
    # Evaluate the iterable
    iterable = self.evaluate(expr.iterable)

    # Check if the expression is iterable
    if not isinstance(iterable, (internals.ObjIterable, internals.ObjIterator)):
      raise internals.InvalidTypeException(f"{iterable} is not iterable")

    # Create a list to store the results
    results = internals.ObjList()

    # Iterate over the iterable
    iterator = iter(iterable) if isinstance(iterable, internals.ObjIterable) else iterable
    iterator.rewind()
    while iterator.advance():
      # Create a new environment with the capture variable
      capture = self.environment.nested()
      capture.declare_variable(expr.variable.name, iterator.current())

      # Evaluate the body
      result = self.evaluate_with(capture, expr.body)
      results.insert(result)

    # Return the results
    return results

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> internals.Obj:
    # Evaluate the iterable
    iterable = self.evaluate(expr.iterable)

    # Check if the expression is traversable
    if not isinstance(iterable, internals.ObjIterable):
      raise internals.InvalidTypeException(f"{iterable} is not iterable")

    # Evaluate the function
    result = expr.function.call(self, expr.variable.name.value, iterable)
    if isinstance(result, internals.ObjIterable):
      return result.as_list()
    else:
      return result

  # Visit a function expression
  def visit_function_expr(self, expr: ast.FunctionExpr) -> internals.Obj:
    # Evaluate the parameters
    def evaluate_parameters(params):
      for param in params:
        # Check for variadic parameters
        if param.variadic:
          yield internals.Parameter(param.name.value, internals.Obj, internals.ParameterVariadic)

        # Check for optional parameters
        elif param.default is not None:
          yield internals.Parameter(param.name.value, internals.Obj, self.evaluate(param.default))

        # Must be a required parameter
        else:
          yield internals.Parameter(param.name.value, internals.Obj)

    # Return the function object
    return internals.ObjFunction(self, internals.Parameters(*evaluate_parameters(expr.params)), expr.body, self.environment)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr: ast.AssignmentExpr) -> internals.Obj:
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Get the distance of the local variable, or otherwise assume it's global
    distance = self.locals.get(expr)
    if distance is not None:
      # Set a local variable
      if self.environment.has_variable(expr.name, distance):
        self.environment.set_variable(expr.name, value, distance)
      else:
        raise internals.RuntimeException(f"Variable '{expr.name.value}' does not exist in the current scope", expr.name.location)

    else:
      # Set a global variable
      if self.globals.has_variable(expr.name):
        self.globals.set_variable(expr.name, value)
      else:
        raise internals.RuntimeException(f"Variable '{expr.name.value}' does not exist in the current scope", expr.name.location)

    # Return the value
    return value

  # Visit a declaration expression
  def visit_declaration_expr(self, expr: ast.DeclarationExpr) -> internals.Obj:
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Declare the value and return it
    if not self.environment.has_variable(expr.name):
      self.environment.declare_variable(expr.name, value)
    else:
      raise internals.RuntimeException(f"Variable '{expr.name.value}' already exists in the current scope", expr.name.location)

    # Return the value
    return value

  # Visit a block expression
  def visit_block_expr(self, expr: ast.BlockExpr) -> internals.Obj:
    # Evaluate the sub-expressions in an environment relative to the CURRENT environment
    return self.evaluate_with(self.environment.nested(), *expr.expressions)

  # Visit a module expression
  def visit_module_expr(self, expr: ast.ModuleExpr) -> internals.Obj:
    # Evaluate the sub-expressions in an environment relative to the GLOBAL environment
    return self.evaluate_with(self.globals.nested(), *expr.expressions)
