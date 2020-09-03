import contextlib
import os.path

from . import ast, internals, output, parser, semantics, transactions


### Definition of the environment ###

# Class that defines an environment
class Environment:
  # Constructor
  def __init__(self, enclosing = None, variables = None):
    self.enclosing = enclosing
    self.variables = variables or internals.ObjRecord()

  # Define a varable
  def define(self, name, value):
    # Define a new variable in the record
    self.variables.set_field(name, value)

  # Assign a variable
  def assign(self, name, value):
    # Set a variable in the record
    if self.variables.has_field(name):
      self.variables.set_field(name, value)

    # Set a variable in the enclosing environment
    elif self.enclosing is not None:
      self.enclosing.assign(name)

    # No matching variable found
    else:
      raise internals.UndefinedField(name)

  # Get a variable
  def get(self, name):
    # Get a variable from the record
    if self.variables.has_field(name):
      return self.variables.get_field(name)

    # Get a variable from the enclosing environment
    elif self.enclosing is not None:
      return self.enclosing.get(name)

    # No matching variable found
    else:
      raise internals.UndefinedField(name)


# Class that defines a global environment
class GlobalEnvironment(Environment):
  # Constructor
  def __init__(self):
    Environment.__init__(self)

    # Add constructor functions
    #self.define('regex', internals.NativeFunction(internals.ObjRegex))

    # Add method functions
    self.define('at', internals.MethodFunction('at', 2))
    self.define('count', internals.MethodFunction('count', 1))
    self.define('eq', internals.ReflectiveMethodFunction('eq', 'eq'))
    self.define('neq', internals.ReflectiveMethodFunction('neq', 'neq'))
    self.define('lt', internals.ReflectiveMethodFunction('lt', 'gte'))
    self.define('lte', internals.ReflectiveMethodFunction('lte', 'gt'))
    self.define('gt', internals.ReflectiveMethodFunction('gt', 'lte'))
    self.define('gte', internals.ReflectiveMethodFunction('gte', 'lt'))
    self.define('match', internals.MethodFunction('match', 2))
    self.define('contains', internals.MethodFunction('contains', 2))

    # Add native functions
    self.define('sum', internals.SumFunction())
    self.define('avg', internals.AvgFunction())

    # Add default collection
    self.define('_', transactions.TransactionList())


### Definition of the interpreter ###

# Class that defines an interpreter
class Interpreter(ast.ExprVisitor, ast.StmtVisitor):
  MAIN_FILE = '__main__'

  # Constructor
  def __init__(self):
    self.cache_analyzer = semantics.CacheAnalyzer(self)
    self.env = GlobalEnvironment()
    self.includes = [self.MAIN_FILE]

  # Create a new lexical scope with the specified variables
  @contextlib.contextmanager
  def scope(self, variables = None):
    # Store the current environment
    previous = self.env

    # Execute the suite
    try:
      # Create a new environment
      self.env = Environment(previous, variables)

      # Yield the previous environment
      yield previous
    finally:
      # Restore the previous environment
      self.env = previous


  # Parse a string into an abstract syntax tree and interpret it
  def execute(self, string):
    try:
      # Parse the string into an abstract syntax tree
      ast = parser.parse(string)

      # Cache literal constants
      self.cache_analyzer.analyze(ast)

      # Interpret the abstract syntax tree
      self.interpret(ast)

    # Catch syntax errors
    except parser.SyntaxError as err:
      print(err)
      print(err.location.point(string, 2))

    # Catch parse errors
    except parser.UnexpectedToken as err:
      print(err)
      print(err.token.location.point(string, 2))

    # Catch runtime errors
    except internals.RuntimeException as err:
      print(f"{err.__class__.__name__}: {err}")

    #except RuntimeError as err:
      #print(err)

  # Include a file
  def execute_include(self, file_name):
    # Check if the file exists
    if not os.path.isfile(file_name):
      raise internals.RuntimeException("The file '{}' could not be found".format(file_name))

    # Add the file to the include stack
    self.includes.append(file_name)

    # Open the file and execute the contents
    with open(file_name, 'r') as file:
      string = file.read()
      self.execute(string)

    # Remove the file from the include stack
    self.includes.pop()

  # Print an object
  def print(self, object):
    print(object)


  ### Definition of the expression visitor functions ###

  # Evaluate an expression
  def evaluate(self, expr):
    return expr.accept(self)

  # Evaluate an expression in a new scope
  def evaluate_scope(self, expr, variables = None):
    with self.scope(variables):
      return self.evaluate(expr)

  # Visit a literal expression
  def visit_literal_expr(self, expr):
    return expr.object

  # Visit a list expression
  def visit_list_expr(self, expr):
    list_object = internals.ObjCollection()
    for item in expr.items:
      list_object.insert(self.evaluate(item))
    return list_object

  # Visit a record expression
  def visit_record_expr(self, expr):
    record_object = internals.ObjRecord()
    for name, expression in expr.fields:
      record_object.set_field(name, self.evaluate(expression))
    return record_object

  # Visit a variable expression
  def visit_variable_expr(self, expr):
    return self.env.get(expr.name)

  # Visit a call expression
  def visit_call_expr(self, expr):
    # Evaluate the callee and arguments
    callee = self.evaluate(expr.callee)
    arguments = [self.evaluate(argument) for argument in expr.arguments]

    # Check if the callee is callable
    if not isinstance(callee, internals.Callable):
      raise internals.RuntimeException(f"The expression '{expr.callee}' is not callable")

    # Check the arity of the callable
    if len(arguments) != callee.arity():
      raise internals.RuntimeException(f"Expected {callee.arity()} arguments but got {len(arguments)}")

    # Call the callable
    return callee.call(self, arguments)

  # Visit a query expression
  def visit_query_expr(self, expr):
    # Evaluate the collection
    collection = self.evaluate(expr.collection)

    # Check if the collection is of the right type
    if not isinstance(collection, internals.ObjCollection):
      raise internals.InvalidTypeException(f"Queries can only operate on collections")

    # Evaluate the clause
    clause_collection = collection
    if expr.clause is not None:
      clause_collection = clause_collection.filter(lambda item: self.evaluate_scope(expr.clause, item))

    # Execute the action
    if expr.action[0] == 'get':
      # Get the item or the specified expression based on the item

      # Map the collection to the specified expression
      if expr.action[1] is not None:
        clause_collection = clause_collection.map(lambda item: self.evaluate_scope(expr.action[1], item))

      # Return the collection
      return clause_collection
    elif expr.action[0] == 'set':
      # Set the fields in the specified record into the item

      # Iterate over the collection
      for item in clause_collection:
        # Evaluate the set record
        set_record = self.evaluate_scope(expr.action[1], item)

        # Check if the record is of the right type
        if not isinstance(set_record, internals.ObjRecord):
          raise internals.InvalidTypeException(f"Set queries can only set records")

        # Apply the record
        for name, value in set_record.fields.items():
          item.set_field(name, value)

      # Return the number of updated items
      return internals.ObjInt(len(clause_collection))
    elif expr.action[0] == 'delete':
      # Delete the items that match the clause from the collection

      # Check if there is a clause
      if expr.clause is None:
        raise internals.RuntimeException(f"Delete queries must provide a clause")

      # Iterate over the collection
      for item in clause_collection:
        # Delete the item from the collection
        collection.delete(item)

      # Return the number of removed items
      return internals.ObjInt(len(clause_collection))
    else:
      raise RuntimeError(f"Invalid query action '{expr.action[0]}'")

  # Visit an assignment expression
  def visit_assignment_expr(self, expr):
    # Evaluate the value
    value = self.evaluate(expr.value)

    # Assign the value and return it
    self.env.assign(expr.name, value)
    return value

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr):
    # Logic operations
    if expr.op == 'not':
      return internals.ObjBool(not self.evaluate(expr.expr).truthy())

    # No matching operation found
    raise ValueError("Undefined unary operator '{}'".format(self.op))

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr):
    # Arithmetic operations
    if expr.op == '*':
      return self.evaluate(expr.left).call('mul', self.evaluate(expr.right))
    elif expr.op == '/':
      return self.evaluate(expr.left).call('div', self.evaluate(expr.right))
    elif expr.op == '+':
      return self.evaluate(expr.left).call('add', self.evaluate(expr.right))
    elif expr.op == '-':
      return self.evaluate(expr.left).call('sub', self.evaluate(expr.right))

    # Comparison operations
    elif expr.op == '<':
      return self.evaluate(expr.left).call('lt', self.evaluate(expr.right))
    elif expr.op == '<=':
      return self.evaluate(expr.left).call('lte', self.evaluate(expr.right))
    elif expr.op == '>':
      return self.evaluate(expr.left).call('gt', self.evaluate(expr.right))
    elif expr.op == '>=':
      return self.evaluate(expr.left).call('gte', self.evaluate(expr.right))
    elif expr.op == '~':
      return self.evaluate(expr.left).call('match', self.evaluate(expr.right))

    # Containment operations
    elif expr.op == 'in':
      return self.evaluate(expr.right).call('contains', self.evaluate(expr.left))

    # Equality operations
    elif expr.op == '==':
      return self.evaluate(expr.left).call('eq', self.evaluate(expr.right))
    elif expr.op == '!=':
      return self.evaluate(expr.left).call('neq', self.evaluate(expr.right))

    # Logic operations
    elif expr.op == 'and':
      return internals.ObjBool(self.evaluate(expr.left).truthy() and self.evaluate(expr.right).truthy())
    elif expr.op == 'or':
      return internals.ObjBool(self.evaluate(expr.left).truthy() or self.evaluate(expr.right).truthy())


  ### Definition of the statement visitor functions ###

  # Interpret a statement
  def interpret(self, stmt):
    stmt.accept(self)

  # Interpret a statement in a new scope
  def interpret_scope(self, stmt, variables = None):
    with self.scope(variables):
      self.interpret(stmt)

  # Visit an expression statement
  def visit_expr_stmt(self, stmt):
    result = self.evaluate(stmt.expr)
    if self.includes[-1] == self.MAIN_FILE:
      print(result)

  # Visit a print statement
  def visit_print_stmt(self, stmt):
    result = self.evaluate(stmt.expr)
    arguments = self.evaluate(stmt.arguments)
    output.print_object(result, **arguments.value())

  # Visit a variable statement
  def visit_variable_stmt(self, stmt):
    value = internals.ObjNull()
    if stmt.value is not None:
      value = self.evaluate(stmt.value)
    self.env.define(stmt.name, value)

  # Visit an include statement
  def visit_include_stmt(self, stmt):
    # Check the types of the arguments
    file_result = self.evaluate(stmt.file)
    if not isinstance(file_result, internals.ObjString):
      raise TypeError(type(file_result))
    file_name = file_result.value

    # Include the file
    self.interpreter.execute_include(file_name)

  # Visit an import statement
  def visit_import_stmt(self, stmt):
    file = self.evaluate(stmt.file)
    arguments = self.evaluate(stmt.arguments)

    if not isinstance(file, internals.ObjString):
      raise TypeError(type(file))
    file_name = file.value()

    # Add the include path to the file
    if self.includes[-1] != self.MAIN_FILE:
      file_name = os.path.join(os.path.split(self.includes[-1])[0], file_name)

    # Add the imported transactions
    new_transactions = transactions.TransactionReader(file_name, **arguments.value())
    self.env.get('_').insert_all(new_transactions)
    print(f"Imported {len(new_transactions)} transactions from '{file_name}'")

  # Visit a block statement
  def visit_block_stmt(self, stmt):
    for sub_stmt in stmt.statements:
      self.interpret(sub_stmt)
