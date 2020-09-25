import os.path

from colorama import Fore, Back, Style

from . import (ast, functions, grammar, internals, output, parser, query,
  semantics, transactions)


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
    if name in self.variables:
      return self.variables[name]

    # Get a variable from the previous environment
    elif self.previous is not None:
      return self.previous[name]

    # No matching variable found
    else:
      raise IndexError(f"Undefined field '{name}'")

  # Set a variable in the environment
  def __setitem__(self, name, value):
    # Set a variable in the current environment
    if name in self.variables:
      self.variables[name] = value

    # Get a variable from the previous environment
    elif self.previous is not None:
      self.previous[name] = value

    # No matching variable found
    else:
      raise KeyError(f"Undefined field '{name}'")

  # Return is a variable exists in the environment
  def __contains__(self, name):
    # Check the current environment
    if name in self.variables:
      return True

    # Check the previous environment
    elif self.previous is not None:
      return name in self.previous

    # No matching variable found
    else:
      return False

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
        return self.variables[name.value]
      else:
        return self.ancestor(distance).variables[name.value]
    except KeyError:
      raise internals.UndefinedFieldException(f"{name.value}", name.location)

  # Set a variable in the environment by means of a lexer token
  def set_variable(self, name, value, distance = 0):
    try:
      if distance == 0:
        self.variables[name.value] = value
      else:
        self.ancestor(distance).variables[name.value] = value
    except KeyError:
      raise internals.UndefinedFieldException(name.value, name.location)

  # Declare a varable in the environment by means of a lexer token
  def declare_variable(self, name, value):
    # Set the variable in the current environment if it doesn't yet exist
    if name.value in self.variables:
      raise internals.RuntimeException(f"Variable '{name.value}' already exists in the current scope", name.location)
    self.variables[name.value] = value

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
    globals['print'] = functions.PrintFunction()
    globals['print_title'] = functions.PrintTitleFunction()
    globals['include'] = functions.IncludeFunction(interpreter)
    globals['import'] = functions.ImportFunction(interpreter)
    globals['_'] = transactions.TransactionList()
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
      if not self.includes[-1] and result is not None:
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

  # Begin a new scope
  def begin_scope(self, variables = None):
    self.environment = Environment(self.environment, variables)

  # End the current scope
  def end_scope(self):
    if self.environment.previous is None:
      raise RuntimeError("Could not end the current scope")
    self.environment = self.environment.previous


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
  def execute_include(self, file_name):
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

  # Import a file
  def execute_import(self, file_name, **keywords):
    # Check if the file exists
    if (resolved_file_name := self.resolve_file_name(file_name)) is None:
      raise internals.RuntimeException(f"Import failed: the file '{file_name}' could not be found")

    # Add the imported transactions
    new_transactions = transactions.TransactionReader(resolved_file_name, **keywords)
    self.environment['_'].insert_all(new_transactions)

    # Return a result object
    return internals.ObjRecord(count = internals.ObjInt(len(new_transactions)))


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
      record_object[name.value] = self.evaluate(value)
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

    # Evaluate the arguments
    args = self.evaluate(expr.arguments.args)
    args_types = [type(arg) for arg in args]
    kwargs = self.evaluate(expr.arguments.kwargs)
    kwargs_types = {name: type(value) for name, value in kwargs}

    required_args = callable.required_args()
    required_kwargs = callable.required_kwargs()

    # Check the length of the arguments
    if len(args_types) != len(required_args):
      raise internals.InvalidCallException(f"Expected {len(required_args)} arguments, got {len(args_types)}", expr.token.location)

    # Iterate over the argument types
    for i, required_type in enumerate(required_args):
      # Check if the argument is the valid type
      if not issubclass(check_type := args_types[i], required_type):
        raise internals.InvalidCallException(f"Expected argument {i+1} of type {required_type}, got type {check_type}", expr.token.location)

    # Iterate over the keyword types
    for name, required_type in required_kwargs.items():
      # Check if the keyword is provided
      if not name in kwargs_types:
        raise internals.InvalidCallException(f"Expected keyword '{name}' of type {required_type}", expr.token.location)

      # Check if the keyword is the valid type
      if not issubclass(check_type := kwargs_types[name], required_type):
        raise internals.InvalidCallException(f"Expected keyword '{name}' of type {required_type}, got type {check_type}", expr.token.location)

    # Call the callable
    return callable(*args._py_list(), **kwargs._py_dict())

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
    raise internals.RuntimeException(f"The expression '{expr.expression}' is either not a record or the specified method is undefined", expr.token.location)

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
      return left.call_method('lt', right)
    elif op == '<=':
      return left.call_method('lte', right)
    elif op == '>':
      return left.call_method('gt', right)
    elif op == '>=':
      return left.call_method('gte', right)
    elif op == '~':
      return left.call_method('match', right)

    # Containment operations
    elif op == 'in':
      return right.call_method('contains', left)

    # Equality operations
    elif op == '==':
      return left.call_method('eq', right)
    elif op == '!=':
      return left.call_method('neq', right)

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

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> internals.Obj:
    # Evaluate the expression
    table = self.evaluate(expr.table)
    predicate = self.evaluate(expr.predicate) if expr.predicate else None

    # Check if the collection is of the right type
    if not isinstance(table, internals.ObjList):
      raise internals.InvalidTypeException(f"Queries can only operate on tables")

    # Check if the predicate, if provided, is a callable
    if predicate and not isinstance(predicate, internals.ObjCallable):
      raise internals.InvalidTypeException(f"A query predicate must be callable")

    # Create a query and execute that
    return query.Query(table, expr.action, predicate).execute(self)

  # Visit a function expression
  def visit_function_expr(self, expr: ast.FunctionExpr) -> internals.Obj:
    return internals.ObjFunction(self, expr, self.environment)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr: ast.AssignmentExpr) -> internals.Obj:
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Get the distance of the local variable, or otherwise assume it's global
    distance = self.locals.get(expr)
    if distance is not None:
      # Get a local variable
      self.environment.set_variable(expr.name, value, distance)
    else:
      # Get a global variable
      self.globals.set_variable(expr.name, value)

    # Return the value
    return value

  # Visit a declaration expression
  def visit_declaration_expr(self, expr: ast.DeclarationExpr) -> internals.Obj:
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Declare the value and return it
    self.environment.declare_variable(expr.name, value)
    return value

  # Visit a block expression
  def visit_block_expr(self, expr: ast.BlockExpr) -> internals.Obj:
    # Evaluate the sub-expressions in an environment relative to the CURRENT environment
    return self.evaluate_with(self.environment.nested(), *expr.expressions)

  # Visit a module expression
  def visit_module_expr(self, expr: ast.ModuleExpr) -> internals.Obj:
    # Evaluate the sub-expressions in an environment relative to the GLOBAL environment
    return self.evaluate_with(self.globals.nested(), *expr.expressions)
