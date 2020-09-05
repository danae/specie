from . import ast


# Class that defines an analyzer that caches literal constants
class CacheAnalyzer(ast.ExprVisitor[None]):
  # Constructor
  def __init__(self, interpreter):
    self.interpreter = interpreter
    self.constants = []


  ### Definition of the expression visitor functions ###

  # Analyze an expression
  def analyze(self, expr: ast.Expr) -> None:
    expr.accept(self)

  # Visit a literal expression
  def visit_literal_expr(self, expr: ast.LiteralExpr) -> None:
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
  def visit_list_expr(self, expr: ast.ListExpr) -> None:
    for item in expr.items:
      self.analyze(item)

  # Visit a record expression
  def visit_record_expr(self, expr: ast.RecordExpr) -> None:
    for name, value in expr.fields:
      self.analyze(value)

  # Visit a variable expression
  def visit_variable_expr(self, expr: ast.VariableExpr) -> None:
    pass

  # Visit a grouping expression
  def visit_grouping_expr(self, expr: ast.GroupingExpr) -> None:
    self.analyze(expr.expression)

  # Visit a call expression
  def visit_call_expr(self, expr: ast.CallExpr) -> None:
    self.analyze(expr.callee)
    self.analyze(expr.arguments.args)
    self.analyze(expr.arguments.kwargs)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr: ast.UnaryOpExpr) -> None:
    self.analyze(expr.expr)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr: ast.BinaryOpExpr) -> None:
    self.analyze(expr.left)
    self.analyze(expr.right)

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> None:
    self.analyze(expr.table)
    self.analyze(expr.action.arguments.args)
    self.analyze(expr.action.arguments.kwargs)
    if expr.predicate:
      self.analyze(expr.predicate)

  # Visit an assignment expression
  def visit_assignment_expr(self, expr: ast.AssignmentExpr) -> None:
    self.analyze(expr.value)

  # Visit a declaration expression
  def visit_declaration_expr(self, expr: ast.DeclarationExpr) -> None:
    self.analyze(expr.value)

  # Visit a block expression
  def visit_block_expr(self, expr: ast.BlockExpr) -> None:
    for expression in expr.expressions:
      self.analyze(expression)


# Class that defines an analyzer that resolves variable accesses
class ResolveAnalyzer(ast.ExprVisitor[None]):
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
