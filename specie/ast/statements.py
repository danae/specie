import os.path

from . import expressions
from .. import internals, interpreter, output, transactions


# Base class that defines any statement
class Stmt:
  pass


# Class that defines an expression statement
class ExprStmt(Stmt):
  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expr!r})"

  def accept(self, visitor):
    visitor.visit_expr_stmt(self)


# Class that defines a variable statement
class VariableStmt(Stmt):
  def __init__(self, name, value):
    self.name = name
    self.value = value

  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.value!r})"

  def accept(self, visitor):
    return visitor.visit_variable_stmt(self)


# Class that defines a print statement
class PrintStmt(Stmt):
  def __init__(self, expr, args):
    self.expr = expr
    self.args = args

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expr!r}, {self.args!r})"

  def accept(self, visitor):
    visitor.visit_print_stmt(self)


# Class that defines an include statement
class IncludeStmt(Stmt):
  def __init__(self, file):
    self.file = file

  def __repr__(self):
    return f"{self.__class__.__name__}({self.file!r})"

  def accept(self, visitor):
    return visitor.visit_include_stmt(self)


# Class that defines an import statement
class ImportStmt(Stmt):
  def __init__(self, file, args):
    self.file = file
    self.args = args

  def __repr__(self):
    return f"{self.__class__.__name__}({self.file!r}, {self.args!r})"

  def accept(self, visitor):
    return visitor.visit_import_stmt(self)


# Class that defines a list statement
class ListStmt(Stmt):
  def __init__(self, expr, args):
    self.expr = expr
    self.args = args

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expr!r}, {self.args!r})"

  def accept(self, visitor):
    return visitor.visit_list_stmt(self)


# Class that defines a table statement
class TableStmt(Stmt):
  def __init__(self, expr, args):
    self.expr = expr
    self.args = args

  def __repr__(self):
    return f"{self.__class__.__name__}({self.expr!r}, {self.args!r})"

  def accept(self, visitor):
    return visitor.visit_table_stmt(self)


# Class that defines a block statement
class BlockStmt(Stmt):
  def __init__(self, statements):
    self.statements = statements

  def __repr__(self):
    return f"{self.__class__.__name__}({self.statements!r})"

  def accept(self, visitor):
    visitor.visit_block_stmt(self)


# Class that defines a statement visitor
class StmtVisitor:
  def visit_expr_stmt(self, stmt):
    raise NotImplementedError()

  def visit_print_stmt(self, stmt):
    raise NotImplementedError()

  def visit_variable_stmt(self, stmt):
    raise NotImplementedError()

  def visit_include_stmt(self, stmt):
    raise NotImplementedError()

  def visit_import_stmt(self, stmt):
    raise NotImplementedError()

  def visit_list_stmt(self, stmt):
    raise NotImplementedError()

  def visit_table_stmt(self, stmt):
    raise NotImplementedError()

  def visit_block_stmt(self, stmt):
    raise NotImplementedError()
