from . import ast, internals


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
    self.analyze(expr.expression)
    self.analyze(expr.arguments.args)
    self.analyze(expr.arguments.kwargs)

  # Visit a get expression
  def visit_get_expr(self, expr: ast.GetExpr) -> None:
    self.analyze(expr.expression)

  # Visit a set expression
  def visit_set_expr(self, expr: ast.SetExpr) -> None:
    self.analyze(expr.value)
    self.analyze(expr.expression)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr: ast.UnaryOpExpr) -> None:
    self.analyze(expr.expression)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr: ast.BinaryOpExpr) -> None:
    self.analyze(expr.left)
    self.analyze(expr.right)

  # Visit a logical expression
  def visit_logical_expr(self, expr: ast.BinaryOpExpr) -> None:
    self.analyze(expr.left)
    self.analyze(expr.right)

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> None:
    self.analyze(expr.table)
    self.analyze(expr.action.arguments.args)
    self.analyze(expr.action.arguments.kwargs)
    if expr.predicate:
      self.analyze(expr.predicate)

  # Visit a function expression
  def visit_function_expr(self, expr: ast.FunctionExpr) -> None:
    self.analyze(expr.body)

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

  # Visit a module expression
  def visit_module_expr(self, expr: ast.ModuleExpr) -> None:
    for expression in expr.expressions:
      self.analyze(expression)


# Class that defines an analyzer that resolves variable accesses
class Resolver(ast.ExprVisitor[None]):
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
  def declare_variable(self, name):
    if not self.scopes:
      return
    self.scopes[-1][name] = False

  # Initialize a variable
  def initialize_variable(self, name):
    if not self.scopes:
      return
    self.scopes[-1][name] = True

  # Resolve a variable
  def resolve_variable(self, expression, name):
    for i in range(len(self.scopes) - 1, -1, -1):
      if name in self.scopes[i]:
        self.interpreter.locals[expression] = len(self.scopes) - 1 - i
        return


  ### Definition of the expression visitor functions ###

  # Resolve an expression
  def resolve(self, expr: ast.Expr) -> None:
    expr.accept(self)

  # Visit a literal expression
  def visit_literal_expr(self, expr: ast.LiteralExpr) -> None:
    pass

  # Visit a list expression
  def visit_list_expr(self, expr: ast.ListExpr) -> None:
    for item in expr.items:
      self.resolve(item)

  # Visit a record expression
  def visit_record_expr(self, expr: ast.RecordExpr) -> None:
    for name, value in expr.fields:
      self.resolve(value)

  # Visit a variable expression
  def visit_variable_expr(self, expr: ast.VariableExpr) -> None:
    if self.scopes and self.scopes[-1].get(expr.name.value) == False:
      raise internals.RuntimeException(f"Cannot read local variable '{expr.name.value}' in its own initializer", expr.name.location)
    self.resolve_variable(expr, expr.name.value)

  # Visit a grouping expression
  def visit_grouping_expr(self, expr: ast.GroupingExpr) -> None:
    self.resolve(expr.expression)

  # Visit a call expression
  def visit_call_expr(self, expr: ast.CallExpr) -> None:
    self.resolve(expr.expression)
    self.resolve(expr.arguments.args)
    self.resolve(expr.arguments.kwargs)

  # Visit a get expression
  def visit_get_expr(self, expr: ast.GetExpr) -> None:
    self.resolve(expr.expression)

  # Visit a set expression
  def visit_set_expr(self, expr: ast.SetExpr) -> None:
    self.resolve(expr.value)
    self.resolve(expr.expression)

  # Visit a unary operator expression
  def visit_unary_op_expr(self, expr: ast.UnaryOpExpr) -> None:
    self.resolve(expr.expression)

  # Visit a binary operator expression
  def visit_binary_op_expr(self, expr: ast.BinaryOpExpr) -> None:
    self.resolve(expr.left)
    self.resolve(expr.right)

  # Visit a logical expression
  def visit_logical_expr(self, expr: ast.BinaryOpExpr) -> None:
    self.resolve(expr.left)
    self.resolve(expr.right)

  # Visit a query expression
  def visit_query_expr(self, expr: ast.QueryExpr) -> None:
    self.resolve(expr.table)
    self.resolve(expr.action.arguments.args)
    self.resolve(expr.action.arguments.kwargs)
    if expr.predicate:
      self.resolve(expr.predicate)

  # Visit a function expression
  def visit_function_expr(self, expr: ast.FunctionExpr) -> None:
    self.begin_scope()
    for parameter in expr.parameters:
      self.declare_variable(parameter.value)
      self.initialize_variable(parameter.value)
    self.resolve(expr.body)
    self.end_scope()

  # Visit an assignment expression
  def visit_assignment_expr(self, expr: ast.AssignmentExpr) -> None:
    self.resolve(expr.value)
    self.resolve_variable(expr, expr.name.value)

  # Visit a declaration expression
  def visit_declaration_expr(self, expr: ast.DeclarationExpr) -> None:
    self.declare_variable(expr.name.value)
    self.resolve(expr.value)
    self.initialize_variable(expr.name.value)

  # Visit a block expression
  def visit_block_expr(self, expr: ast.BlockExpr) -> None:
    self.begin_scope()
    for expression in expr.expressions:
      self.resolve(expression)
    self.end_scope()

  # Visit a module expression
  def visit_module_expr(self, expr: ast.ModuleExpr) -> None:
    self.begin_scope()
    for expression in expr.expressions:
      self.resolve(expression)
    self.end_scope()
