from typing import TypeVar, Generic


#####################################
### Definition of the expressions ###
#####################################

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.object!r})"

  def accept(self, visitor):
    return visitor.visit_literal_expr(self)


# Class that defines a list expression
class ListExpr(Expr):
  def __init__(self, items = None):
    self.items = items if items is not None else []

  def __str__(self):
    return '[' + ', '.join(f"{item}" for item in self.items) + ']'

  def __repr__(self):
    return f"{self.__class__.__name__}({self.items!r})"

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
  def __init__(self, fields = None):
    self.fields = fields if fields is not None else []

  def __str__(self):
    return '{' + ', '.join(f"{name.value}: {value}" for name, value in self.fields) + '}'

  def __repr__(self):
    return f"{self.__class__.__name__}({self.fields!r})"

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r})"

  def accept(self, visitor):
    return visitor.visit_variable_expr(self)


# Class that defines a grouping expression
class GroupingExpr(Expr):
  def __init__(self, expression):
    self.expression = expression

  def __str__(self):
    return f"({self.expression})"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expression!r})"

  def accept(self, visitor):
    return visitor.visit_grouping_expr(self)


# Class that defines a call expression
class CallExpr(Expr):
  def __init__(self, expression, token, args):
    self.expression = expression
    self.token = token
    self.args = args

  def __str__(self):
    return f"{self.expression}(" + ', '.join(f"{arg}" for arg in self.args) + ")"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expression!r}, {self.token!r}, {self.args!r})"

  def accept(self, visitor):
    return visitor.visit_call_expr(self)


# Class that defines a get expression
class GetExpr(Expr):
  def __init__(self, expression, token, name):
    self.expression = expression
    self.token = token
    self.name = name

  def __str__(self):
    return f"{self.expression}.{self.name.value}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expression!r}, {self.token!r}, {self.name!r})"

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
    return f"{self.expression}.{self.name.value} {self.op} {self.value}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expression!r}, {self.token!r}, {self.name!r}, {self.op!r}, {self.value!r})"

  def accept(self, visitor):
    return visitor.visit_set_expr(self)


# Class that defines an unary operator expression
class UnaryOpExpr(Expr):
  def __init__(self, op, expression):
    self.op = op
    self.expression = expression

  def __str__(self):
    return f"{self.op.value} {self.expression}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.op!r}, {self.expression!r})"

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.left!r}, {self.op!r}, {self.right!r})"

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.left!r}, {self.op!r}, {self.right!r})"

  def accept(self, visitor):
    return visitor.visit_logical_expr(self)


# Class that defines an if expression
class IfExpr(Expr):
  def __init__(self, condition, then_clause, else_clause):
    self.condition = condition
    self.then_clause = then_clause
    self.else_clause = else_clause

  def __str__(self):
    if self.else_clause is not None:
      return f"if {self.condition} then {self.then_clause} else {self.else_clause}"
    else:
      return f"if {self.condition} then {self.then_clause}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.condition!r}, {self.then_clause}, {self.else_clause!r})"

  def accept(self, visitor):
    return visitor.visit_if_expr(self)


# Class that defines a for expression
class ForExpr(Expr):
  def __init__(self, variable, iterable, body):
    self.variable = variable
    self.iterable = iterable
    self.body = body

  def __str__(self):
    return f"for {self.variable} in {self.iterable} {self.body}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.variable!r}, {self.iterable}, {self.body!r})"

  def accept(self, visitor):
    return visitor.visit_for_expr(self)


# Class that defines a query expression
class QueryExpr(Expr):
  def __init__(self, variable, iterable, function):
    self.variable = variable
    self.iterable = iterable
    self.function = function

  def __str__(self):
    return f"from {self.variable} in {self.iterable} {self.function}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.variable!r}, {self.iterable!r}, {self.function!r})"

  def accept(self, visitor):
    return visitor.visit_query_expr(self)


# Class that defines a function expression
class FunctionExpr(Expr):
  def __init__(self, params, body):
    self.params = params
    self.body = body

  def __str__(self):
    return '(' + ', '.join(param.value for param in self.params) + ') -> ' + f"{self.body}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.params!r}, {self.body!r})"

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.op!r}, {self.value!r})"

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

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.op!r}, {self.value!r})"

  def accept(self, visitor):
    return visitor.visit_declaration_expr(self)


# Class that defines a block expression
class BlockExpr(Expr):
  def __init__(self, expressions):
    self.expressions = expressions

  def __str__(self):
    return "do\n" + "\n".join(f"{expression}" for expression in self.expressions) + "\nend"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expressions!r})"

  def accept(self, visitor):
    return visitor.visit_block_expr(self)


# Class that defines a module expression
class ModuleExpr(Expr):
  def __init__(self, expressions):
    self.expressions = expressions

  def __str__(self):
    return "\n".join(f"{expression}" for expression in self.expressions)

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expressions!r})"

  def accept(self, visitor):
    return visitor.visit_module_expr(self)

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

  def visit_if_expr(self, expr: IfExpr) -> T:
    raise NotImplementedError()

  def visit_for_expr(self, expr: ForExpr) -> T:
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

  def visit_module_expr(self, expr: ModuleExpr) -> T:
    raise NotImplementedError()
