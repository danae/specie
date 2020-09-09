from typing import TypeVar, Generic


### Definition of helper classes

# Class that holds a set of arguments and keywords
class Arguments:
  # Constructor
  def __init__(self, args, kwargs):
    self.args = args
    self.kwargs = kwargs

  # Convert to string
  def __str__(self):
    string = ""
    if self.args:
      string += str(self.args)[1:-1]
    if self.kwargs:
      string += (', ' if string else '') + str(self.kwargs)[1:-1]
    return string

  # Convert to boolean
  def __bool__(self):
    return bool(self.args) and bool(self.kwargs)


# Class that holds a
class Call:
  # Constructor
  def __init__(self, name, arguments):
    self.name = name
    self.arguments = arguments

  # Convert to string
  def __str__(self):
    if self.arguments:
      return f"{self.name.value} {self.arguments}"
    else:
      return f"{self.name.value}"


### Definition of the expressions ###

# Base class for an abstract sytax tree expression
class Expr:
  # Accept a visitor on this expression
  def accept(self, visitor):
    raise NotImplementedError()


# Class that defines a literal expression
class LiteralExpr(Expr):
  def __init__(self, object):
    self.object = object

  def __str__(self):
    return str(self.object)

  def accept(self, visitor):
    return visitor.visit_literal_expr(self)


# Class that defines a list expression
class ListExpr(Expr):
  def __init__(self, items = []):
    self.items = items

  def __str__(self):
    return '[' + ', '.join(f"{item}" for item in self.items) + ']'

  def __getitem__(self, index):
    return self.items[index]

  def __len__(self):
    return len(self.items)

  def __iter__(self):
    return iter(self.items)

  def accept(self, visitor):
    return visitor.visit_list_expr(self)


# Class that defines a record expression
class RecordExpr(Expr):
  def __init__(self, fields = []):
    self.fields = fields

  def __str__(self):
    return '{' + ', '.join(f"{name.value}: {value}" for name, value in self.fields) + '}'

  def __getitem__(self, index):
    return self.fields[index]

  def __len__(self):
    return len(self.fields)

  def __iter__(self):
    return iter(self.fields)

  def accept(self, visitor):
    return visitor.visit_record_expr(self)


# Class that defines a variable expression
class VariableExpr(Expr):
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name.value

  def accept(self, visitor):
    return visitor.visit_variable_expr(self)


# Class that defines a grouping expression
class GroupingExpr(Expr):
  def __init__(self, expression):
    self.expression = expression

  def __str__(self):
    return f"({self.expression})"

  def accept(self, visitor):
    return visitor.visit_grouping_expr(self)


# Class that defines a call expression
class CallExpr(Expr):
  def __init__(self, expression, token, arguments):
    self.expression = expression
    self.token = token
    self.arguments = arguments

  def __str__(self):
    return f"{self.expression}({self.arguments})"

  def accept(self, visitor):
    return visitor.visit_call_expr(self)


# Class that defines a get expression
class GetExpr(Expr):
  def __init__(self, expression, token, name):
    self.expression = expression
    self.token = token
    self.name = name

  def __str__(self):
    return f"{self.expression}.{self.name}"

  def accept(self, visitor):
    return visitor.visit_get_expr(self)


# Class that defines a set expression
class SetExpr(Expr):
  def __init__(self, expression, token, name, op, value):
    self.expression = expression
    self.token = token
    self.name = name
    self.op = op
    self.value = value

  def __str__(self):
    return f"{self.expression}.{self.name} {self.op} {self.value}"

  def accept(self, visitor):
    return visitor.visit_set_expr(self)


# Class that defines an unary operator expression
class UnaryOpExpr(Expr):
  def __init__(self, op, expr):
    self.op = op
    self.expr = expr

  def __str__(self):
    return f"{self.op.value} {self.expr}"

  def accept(self, visitor):
    return visitor.visit_unary_op_expr(self)


# Class that defines a binary operator expression
class BinaryOpExpr(Expr):
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right

  def __str__(self):
    return f"{self.left} {self.op.value} {self.right}"

  def accept(self, visitor):
    return visitor.visit_binary_op_expr(self)


# Class that defines a logical expression
class LogicalExpr(Expr):
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right

  def __str__(self):
    return f"{self.left} {self.op.value} {self.right}"

  def accept(self, visitor):
    return visitor.visit_logical_expr(self)


# Class that defines a query expression
class QueryExpr(Expr):
  def __init__(self, table, action, predicate):
    self.table = table
    self.action = action
    self.predicate = predicate

  def __str__(self):
    if self.predicate:
      return f"from {self.table} {self.action} if {self.predicate}"
    else:
      return f"from {self.table} {self.action}"

  def accept(self, visitor):
    return visitor.visit_query_expr(self)


# Class that defines a function expression
class FunctionExpr(Expr):
  def __init__(self, parameters, body):
    self.parameters = parameters
    self.body = body

  def __str__(self):
    return '(' + ', '.join(parameter.value for parameter in self.parameters) + '): ' + f"{self.body}"

  def accept(self, visitor):
    return visitor.visit_function_expr(self)


# Class that defines an assignment expression
class AssignmentExpr(Expr):
  def __init__(self, name, op, value):
    self.name = name
    self.op = op
    self.value = value

  def __str__(self):
    return f"{self.name.value} {self.op.value} {self.value}"

  def accept(self, visitor):
    return visitor.visit_assignment_expr(self)


# Class that defines an declaration expression
class DeclarationExpr(Expr):
  def __init__(self, name, op, value):
    self.name = name
    self.op = op
    self.value = value

  def __str__(self):
    return f"var {self.name.value} {self.op.value} {self.value}"

  def accept(self, visitor):
    return visitor.visit_declaration_expr(self)


# Class that defines a block expression
class BlockExpr(Expr):
  def __init__(self, expressions):
    self.expressions = expressions

  def __str__(self):
    return "do\n" + "\n".join(f"{expression}" for expression in self.expressions) + "\nend"

  def accept(self, visitor):
    return visitor.visit_block_expr(self)


### Definition of the expression visitor ###

# Create a generic type variable for the expression visitor
T = TypeVar('T')

# Class that defines an expression visitor
class ExprVisitor(Generic[T]):
  def visit_literal_expr(self, expr: LiteralExpr) -> T:
    raise NotImplementedError()

  def visit_list_expr(self, expr: ListExpr) -> T:
    raise NotImplementedError()

  def visit_record_expr(self, expr: RecordExpr) -> T:
    raise NotImplementedError()

  def visit_variable_expr(self, expr: VariableExpr) -> T:
    raise NotImplementedError()

  def visit_grouping_expr(self, expr: GroupingExpr) -> T:
    raise NotImplementedError()

  def visit_call_expr(self, expr: CallExpr) -> T:
    raise NotImplementedError()

  def visit_get_expr(self, expr: GetExpr) -> T:
    raise NotImplementedError()

  def visit_set_expr(self, expr: SetExpr) -> T:
    raise NotImplementedError()

  def visit_unary_op_expr(self, expr: UnaryOpExpr) -> T:
    raise NotImplementedError()

  def visit_binary_op_expr(self, expr: BinaryOpExpr) -> T:
    raise NotImplementedError()

  def visit_logical_expr(self, expr: LogicalExpr) -> T:
    raise NotImplementedError()

  def visit_query_expr(self, expr: QueryExpr) -> T:
    raise NotImplementedError()

  def visit_function_expr(self, expr: FunctionExpr) -> T:
    raise NotImplementedError()

  def visit_assignment_expr(self, expr: AssignmentExpr) -> T:
    raise NotImplementedError()

  def visit_declaration_expr(self, expr: DeclarationExpr) -> T:
    raise NotImplementedError()

  def visit_block_expr(self, expr: BlockExpr) -> T:
    raise NotImplementedError()
