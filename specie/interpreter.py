import os.path

from colorama import Fore, Back, Style

from . import ast, functions, internals, output, parser, query, semantics, transactions


### Definition of the environment ###

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

    # Set a variable in the previous environment
    elif self.previous is not None:
      self.previous[name] = value

    # No matching variable found
    else:
      raise IndexError(f"Undefined field '{name}'")

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

  # Get a variable in the environment by means of a lexer token
  def get_variable(self, name):
    try:
      return self[name.value]
    except IndexError:
      raise internals.UndefinedFieldException(name.value, name.location)

  # Set a variable in the environment by means of a lexer token
  def set_variable(self, name, value):
    try:
      self[name.value] = value
    except IndexError:
      raise internals.UndefinedFieldException(name.value, name.location)

  # Declare a varable in the environment by means of a lexer token
  def declare_variable(self, name, value):
    # Set the variable in the current environment if it doesn't yet exist
    if name.value in self.variables:
      raise internals.RuntimeException(f"Variable '{name.value}' already exists in the current scope", name.location)
    self.variables[name.value] = value

  # Return a global environment
  @classmethod
  def globals(cls):
    globals = internals.ObjRecord()
    globals['print'] = functions.PrintFunction()
    globals['print_title'] = functions.PrintTitleFunction()
    globals['include'] = functions.IncludeFunction()
    globals['import'] = functions.ImportFunction()
    globals['_'] = transactions.TransactionList()
    return cls(None, globals)


### Definition of the interpreter ###

# Class that defines an interpreter
class Interpreter(ast.ExprVisitor[internals.Obj]):
  # Constructor
  def __init__(self):
    # Define the environment
    self.globals = Environment.globals()
    self.environment = self.globals

    # Define the include stack; the first file is the interactive console
    self.includes = [None]

    # Define the static analyzers
    self.cache_analyzer = semantics.CacheAnalyzer(self)

  # Parse a string into an abstract syntax tree and interpret it
  def execute(self, string):
    # Check if the string is empty
    if not string.strip():
      return

    # Parse and interpret the string
    try:
      # Parse the string into an abstract syntax tree
      ast = parser.parse(string)

      # Cache literal constants
      self.cache_analyzer.analyze(ast)

      # Interpret the abstract syntax tree
      result = self.evaluate(ast)
      if not self.includes[-1] and result is not None:
        output.print_object(result)

    # Catch syntax errors
    except parser.SyntaxError as err:
      if self.includes[-1]:
        print(f"In file '{self.includes[-1]}':")
      print(f"{Style.BRIGHT}{Fore.RED}{err}{Style.RESET_ALL}")
      print(err.location.point(string, 2))

    # Catch unexpected token errors
    except parser.UnexpectedToken as err:
      if self.includes[-1]:
        print(f"In file '{self.includes[-1]}':")
      print(f"{Style.BRIGHT}{Fore.RED}{err}{Style.RESET_ALL}")
      print(err.token.location.point(string, 2))

    # Catch runtime errors
    except internals.RuntimeException as err:
      if self.includes[-1]:
        print(f"In file '{self.includes[-1]}':")
      print(f"{Style.BRIGHT}{Fore.RED}{err}{Style.RESET_ALL}")
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

  # Begin an included file
  def begin_include(self, file):
    self.includes.append(file)

  # End an included file
  def end_include(self):
    if not self.includes:
      raise RuntimeError("Could not end the current included file")
    self.includes.pop()

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


  ### Definition of native functions ###

  # Include a file
  def execute_include(self, file_name):
    # Check if the file exists
    if (resolved_file_name := self.resolve_file_name(file_name)) is None:
      raise internals.RuntimeException(f"Include failed: the file '{file_name}' could not be found")

    # Add the file to the include stack
    self.begin_include(resolved_file_name)
    self.begin_scope()

    # Open the file and execute the contents
    with open(resolved_file_name, 'r') as file:
      string = file.read()
      self.execute(string)

    # Get the current defined variables
    variables = self.environment.variables

    # Remove the file from the include stack
    self.end_scope()
    self.end_include()

    # Return the variables
    return variables

  # Import a file
  def execute_import(self, file_name, **keywords):
    # Check if the file exists
    if (resolved_file_name := self.resolve_file_name(file_name)) is None:
      raise internals.RuntimeException(f"Import failed: the file '{file_name}' could not be found")

    # Add the imported transactions
    new_transactions = transactions.TransactionReader(resolved_file_name, **keywords)
    self.environment['_'].insert_all(new_transactions)

    # Return a result object
    result = internals.ObjRecord()
    result['count'] = internals.ObjInt(len(new_transactions))
    return result


  ### Definition of the expression visitor functions ###

  # Evaluate an expression
  def evaluate(self, expr: ast.Expr) -> internals.Obj:
    return expr.accept(self)

  # Evaluate an expression in a new scope
  def evaluate_scope(self, expr: ast.Expr, locals = None) -> internals.Obj:
    self.begin_scope(locals)
    result = self.evaluate(expr)
    self.end_scope()

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
    return self.environment.get_variable(expr.name)

  # Visit a grouping expression
  def visit_grouping_expr(self, expr: ast.GroupingExpr) -> internals.Obj:
    return self.evaluate(expr.expression)

  # Visit a call expression
  def visit_call_expr(self, expr: ast.CallExpr) -> internals.Obj:
    # Evaluate the expression
    callee = self.evaluate(expr.callee)
    args = self.evaluate(expr.arguments.args)
    kwargs = self.evaluate(expr.arguments.kwargs)

    # Check if the callee is callable
    if not isinstance(callee, internals.Callable):
      raise internals.RuntimeException(f"The expression '{expr.callee}' is not callable", expr.paren.location)

    # Check the signature of the callable
    signature = callee.signature()

    # Check the arguments
    # TODO: Print correct types instead of internal names
    args_types = [type(arg) for arg in args]
    if len(args_types) != len(signature.args_types):
      raise internals.InvalidCallException(f"Expected {len(signature.arguments_types)} arguments, got {len(argument_types)}", expr.paren.location)
    for i, arg_type in enumerate(signature.args_types):
      # Check if the argument is the valid type
      if not issubclass(check_type := args_types[i], arg_type):
        raise internals.InvalidCallException(f"Expected argument {i+1} of type {arg_type}, got type {check_type}", expr.paren.location)

    # Check the keywords
    # TODO: Print correct types instead of internal names
    kwargs_types = {name: type(value) for name, value in kwargs}
    for name, kwarg_type in signature.kwargs_types.items():
      # Check if the keyword is provided
      if not name in kwargs_types:
        raise internals.InvalidCallException(f"Expected keyword '{name}' of type {kwarg_type}", expr.paren.location)
      # Check if the keyword is the valid type
      if not issubclass(check_type := kwargs_types[name], kwarg_type):
        raise internals.InvalidCallException(f"Expected keyword '{name}' of type {kwarg_type}, got type {check_type}", expr.paren.location)

    # Call the callable
    return callee.call(self, args, kwargs)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr: ast.UnaryOpExpr) -> internals.Obj:
    op = expr.op.value

    # Logic operations
    if op == 'not':
      return internals.ObjBool(not self.evaluate(expr.expr).truthy())

    # No matching operation found
    raise internals.RuntimeException("Undefined unary operator '{}'".format(op), expr.op.location)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr: ast.BinaryOpExpr) -> internals.Obj:
    op = expr.op.value

    # Arithmetic operations
    if op == '*':
      return self.evaluate(expr.left).call('mul', self.evaluate(expr.right))
    elif op == '/':
      return self.evaluate(expr.left).call('div', self.evaluate(expr.right))
    elif op == '+':
      return self.evaluate(expr.left).call('add', self.evaluate(expr.right))
    elif op == '-':
      return self.evaluate(expr.left).call('sub', self.evaluate(expr.right))

    # Comparison operations
    elif op == '<':
      return self.evaluate(expr.left).call('lt', self.evaluate(expr.right))
    elif op == '<=':
      return self.evaluate(expr.left).call('lte', self.evaluate(expr.right))
    elif op == '>':
      return self.evaluate(expr.left).call('gt', self.evaluate(expr.right))
    elif op == '>=':
      return self.evaluate(expr.left).call('gte', self.evaluate(expr.right))
    elif op == '~':
      return self.evaluate(expr.left).call('match', self.evaluate(expr.right))

    # Containment operations
    elif op == 'in':
      return self.evaluate(expr.right).call('contains', self.evaluate(expr.left))

    # Equality operations
    elif op == '==':
      return self.evaluate(expr.left).call('eq', self.evaluate(expr.right))
    elif op == '!=':
      return self.evaluate(expr.left).call('neq', self.evaluate(expr.right))

    # Logic operations
    elif op == 'and':
      return internals.ObjBool(self.evaluate(expr.left).truthy() and self.evaluate(expr.right).truthy())
    elif op == 'or':
      return internals.ObjBool(self.evaluate(expr.left).truthy() or self.evaluate(expr.right).truthy())

    # No matching operation found
    raise internals.RuntimeException("Undefined binary operator '{}'".format(op), expr.op.location)

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> internals.Obj:
    # Evaluate the table
    table = self.evaluate(expr.table)

    # Check if the collection is of the right type
    if not isinstance(table, internals.ObjList):
      raise internals.InvalidTypeException(f"Queries can only operate on tables")

    # Create a query and execute that
    q = query.Query(table, expr.action, expr.predicate)
    return q.execute(self)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr: ast.AssignmentExpr) -> internals.Obj:
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Set the value and return it
    self.environment.set_variable(expr.name, value)
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
    result = None

    # Start a new scope if applicable
    if expr.new_scope:
      self.begin_scope()

    # Evaluate the sub-expressions
    for expression in expr.expressions:
      result = self.evaluate(expression)

    # End the current scope if applicable
    if expr.new_scope:
      self.end_scope()

    # Return the last result
    return result
