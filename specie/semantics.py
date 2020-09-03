from . import ast


# Class that defines an analyzer that caches literal constants
class CacheAnalyzer(ast.ExprVisitor, ast.StmtVisitor):
  # Constructor
  def __init__(self, interpreter):
    self.interpreter = interpreter
    self.constants = []

  # Analyze a statement or expression
  def analyze(self, expr_or_stmt):
    expr_or_stmt.accept(self)


  ### Definition of the expression visitor functions ###

  # Visit a literal expression
  def visit_literal_expr(self, expr):
    try:
      # Check if the literal value is already in the list of constants
      index = self.constants.index(expr.object)
    except ValueError:
      # Add the object to the list of constants
      self.constants.append(expr.object)
    else:
      # Update the object with the value from the list of constants
      expr.object = self.constants[self.constants.index(expr.object)]

  # Visit a list expression
  def visit_list_expr(self, expr):
    for item in expr.items:
      self.analyze(item)

  # Visit a record expression
  def visit_record_expr(self, expr):
    for name, value in expr.fields:
      self.analyze(value)

  # Visit a variable expression
  def visit_variable_expr(self, expr):
    pass

  # Visit a call expression
  def visit_call_expr(self, expr):
    self.analyze(expr.callee)
    for argument in expr.arguments:
      self.analyze(argument)

  # Visit a query expression
  def visit_query_expr(self, expr):
    self.analyze(expr.collection)
    # TODO: Anayze the action
    if expr.clause:
      self.analyze(expr.clause)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr):
    self.analyze(expr.value)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr):
    self.analyze(expr.expr)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr):
    self.analyze(expr.left)
    self.analyze(expr.right)


  ### Definition of the statement visitor functions ###

  # Visit an expression statement
  def visit_expr_stmt(self, stmt):
    self.analyze(stmt.expr)

  # Visit a print statement
  def visit_print_stmt(self, stmt):
    self.analyze(stmt.expr)
    self.analyze(stmt.arguments)

  # Visit a variable statement
  def visit_variable_stmt(self, stmt):
    self.analyze(stmt.value)

  # Visit an include statement
  def visit_include_stmt(self, stmt):
    self.analyze(stmt.file)

  # Visit an import statement
  def visit_import_stmt(self, stmt):
    self.analyze(stmt.file)
    self.analyze(stmt.arguments)

  # Visit a block statement
  def visit_block_stmt(self, stmt):
    for statement in stmt.statements:
      self.analyze(statement)


# Class that defines an analyzer that resolves variable accesses
class ResolveAnalyzer(ast.ExprVisitor, ast.StmtVisitor):
  # Constructor
  def __init__(self, interpreter):
    self.interpreter = interpreter

    # The scope stack holds a dictionary (name: str, initialized: bool) for each scope
    self.scopes = []

  # Push a new scope onto the scopes stack
  def begin_scope(self):
    self.scopes.append({})

  # Pop the current scope from the scopes stack
  def end_scope(self):
    self.scopes.pop()

  # Declare a variable
  def declare(self, name):
    if not self.scopes:
      return
    self.scopes[-1][name] = False

  # Define a variable
  def define(self, name):
    if not self.scopes:
      return
    self.scopes[-1][name] = True

  # Resolve a local expression
  def resolve_local(self, expr, name):
    for i in range(len(self.scopes)):
      if name in scopes[-i]:
        interpreter.resolve(expr, i)

  # Resulve an expression
  def resolve_expr(self, expr):
    expr.accept(this)

  # Resolve a statement
  def resolve_stmt(self, stmt):
    stmt.accept(self)


  ### Definition of the expression visitor functions ###

  # Visit a literal expression
  def visit_literal_expr(self, expr):
    pass

  # Visit a list expression
  def visit_list_expr(self, expr):
    for item in expr.items:
      self.resolve_expr(item)

  # Visit a record expression
  def visit_record_expr(self, expr):
    for name, value in expr.fields:
      self.resolve_expr(value)

  # Visit a variable expression
  def visit_variable_expr(self, expr):
    if self.scopes and self.scopes[-1].get(expr.name, None) == False:
      raise RuntimeError("Cannot read local variable in its own intializer")
    self.resolve_local(expr, exp.name)

  # Visit a call expression
  def visit_call_expr(self, expr):
    self.resolve_expr(expr.callee)
    for argument in expr.arguments:
      self.resolve_expr(argument)

  # Visit a query expression
  def visit_query_expr(self, expr):
    self.resolve_expr(expr.collection)
    # TODO: resolve the action
    self.resolve_expr(expr.clause)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr):
    self.resolve_expr(expr.value)
    self.resolve_local(expr, expr.name)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr):
    self.resolve_expr(expr.expr)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr):
    self.resolve_expr(expr.left)
    self.resolve_expr(expr.right)


  ### Definition of the statement visitor functions ###

  # Visit an expression statement
  def visit_expr_stmt(self, stmt):
    self.resolve_expr(stmt.expr)

  # Visit a print statement
  def visit_print_stmt(self, stmt):
    self.resolve_expr(stmt.expr)

  # Visit a variable statement
  def visit_variable_stmt(self, stmt):
    self.declare(stmt.name)
    if stmt.value is not None:
      self.resolve_expr(stmt.value)
    self.define(stmt.name)

  # Visit an include statement
  def visit_include_stmt(self, stmt):
    self.resolve_expr(stmt.file)

  # Visit an import statement
  def visit_import_stmt(self, stmt):
    self.resolve_expr(stmt.file)

  # Visit a block statement
  def visit_block_stmt(self, stmt):
    self.begin_scope()
    for statement in stmt.statements:
      self.resolve_stmt(statement)
    self.end_scope()
