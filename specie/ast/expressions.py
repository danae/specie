from .. import internals


# Base class for an abstract sytax tree expression
class Expr:
  pass


# Class that defines a literal expression
class LiteralExpr(Expr):
  def __init__(self, object):
    self.object = object

  def __repr__(self):
    return f"{self.__class__.__name__}({self.object!r})"

  def accept(self, visitor):
    return visitor.visit_literal_expr(self)


# Class that defines a list expression
class ListExpr(Expr):
  def __init__(self, items = []):
    self.items = items

  def __repr__(self):
    return f"{self.__class__.__name__}({self.items!r})"

  def accept(self, visitor):
    return visitor.visit_list_expr(self)


# Class that defines a record expression
class RecordExpr(Expr):
  def __init__(self, fields = []):
    self.fields = fields

  def __repr__(self):
    return f"{self.__class__.__name__}({self.fields!r})"

  def accept(self, visitor):
    return visitor.visit_record_expr(self)


# Class that defines a variable expression
class VariableExpr(Expr):
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r})"

  def accept(self, visitor):
    return visitor.visit_variable_expr(self)


# Class that defines a call expression
class CallExpr(Expr):
  def __init__(self, callee, arguments):
    self.callee = callee
    self.arguments = arguments

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expr!r}, {self.arguments!r})"

  def accept(self, visitor):
    return visitor.visit_call_expr(self)


# Class that defines a query expression
class QueryExpr(Expr):
  def __init__(self, collection, action, clause):
    self.collection = collection
    self.action = action
    self.clause = clause

  def __repr__(self):
    return f"{self.__class__.__name__}({self.collection!r}, {self.action!r}, {self.clause!r})"

  def accept(self, visitor):
    return visitor.visit_query_expr(self)


# Class that defines an assignment expression
class AssignmentExpr(Expr):
  def __init__(self, name, value):
    self.name = name
    self.value = value

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.value!r})"

  def accept(self, visitor):
    return visitor.visit_assignment_expr(self)


# Class that defines an unary operator expression
class UnaryOpExpr(Expr):
  def __init__(self, op, expr):
    self.op = op
    self.expr = expr

  def __repr__(self):
    return f"{self.__class__.__name__}({self.op!r}, {self.expr!r})"

  def accept(self, visitor):
    return visitor.visit_unary_op_expr(self)


# Class that defines a binary operator expression
class BinaryOpExpr(Expr):
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right

  def __repr__(self):
    return f"{self.__class__.__name__}({self.left!r}, {self.op!r}, {self.right!r})"

  def accept(self, visitor):
    return visitor.visit_binary_op_expr(self)


# Class that defines an expression visitor
class ExprVisitor:
  def visit_literal_expr(self, expr):
    raise NotImplementedError()

  def visit_list_expr(self, expr):
    raise NotImplementedError()

  def visit_record_expr(self, expr):
    raise NotImplementedError()

  def visit_variable_expr(self, expr):
    raise NotImplementedError()

  def visit_call_expr(self, expr):
    raise NotImplementedError()

  def visit_query_expr(self, expr):
    raise NotImplementedError()

  def visit_assignment_expr(self, expr):
    raise NotImplementedError()

  def visit_unary_op_expr(self, expr):
    raise NotImplementedError()

  def visit_binary_op_expr(self, expr):
    raise NotImplementedError()
