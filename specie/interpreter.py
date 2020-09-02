import contextlib
import os.path

from . import ast, internals, output, parser, transactions


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


### Definition of the interpreter ###

# Class that defines an interpreter
class Interpreter(ast.ExprVisitor, ast.StmtVisitor):
  MAIN_FILE = '__main__'

  # Constructor
  def __init__(self):
    self.env = Environment()
    self.includes = [self.MAIN_FILE]

    # Add default collection
    self.env.define('_', transactions.TransactionList())

    # Add native functions
    self.env.define('at', internals.MethodFunction('at', 2))
    self.env.define('count', internals.MethodFunction('count', 1))
    self.env.define('eq', internals.ReflectiveMethodFunction('eq', 'eq'))
    self.env.define('neq', internals.ReflectiveMethodFunction('neq', 'neq'))
    self.env.define('lt', internals.ReflectiveMethodFunction('lt', 'gte'))
    self.env.define('lte', internals.ReflectiveMethodFunction('lte', 'gt'))
    self.env.define('gt', internals.ReflectiveMethodFunction('gt', 'lte'))
    self.env.define('gte', internals.ReflectiveMethodFunction('gte', 'lt'))
    self.env.define('match', internals.MethodFunction('match', 2))
    self.env.define('contains', internals.MethodFunction('contains', 2))

    self.env.define('sum', internals.SumFunction())
    self.env.define('avg', internals.AvgFunction())

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
    # Parse and interpret the string
    try:
      ast = parser.parse(string)
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


  ### Definition of the expression visitor ###

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
    def evaluate_clause(item):
      return self.evaluate_scope(expr.clause, item)

    clause_collection = collection
    if expr.clause is not None:
      clause_collection = clause_collection.filter(evaluate_clause)

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


  ### Definition of the statement visitor ###

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
    args = {key: self.evaluate(value) for key, value in stmt.args.items()}

    output.print_object(result, **args)

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
    # TODO: Implement logic for objects instead of their values
    args = {key: self.evaluate(value).value for key, value in stmt.args.items()}
    if not isinstance(file, internals.ObjString):
      raise TypeError(file)
    file_name = str(file)

    # Add the include path to the file
    if self.includes[-1] != self.MAIN_FILE:
      file_name = os.path.join(os.path.split(self.includes[-1])[0], file_name)

    # Add the imported transactions
    new_transactions = transactions.TransactionReader(file_name, **args)
    self.env.get('_').insert_all(new_transactions)
    print(f"Imported {len(new_transactions)} transactions from '{file_name}'")

  """
  # Visit a list statement
  def visit_list_stmt(self, stmt):
    o = output.ListOutput(stmt.expr, **stmt.args)
    o.print(self.env.get('_'))

  # Visit a table statement
  def visit_table_stmt(self, stmt):
    o = output.TableOutput(stmt.expr, **stmt.args)
    o.print(self.env.get('_'))
  """

  # Visit a block statement
  def visit_block_stmt(self, stmt):
    for sub_stmt in stmt.statements:
      self.interpret(sub_stmt)
