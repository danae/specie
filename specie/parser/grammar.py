from functools import reduce

from . import lexer
from .. import ast, internals

from .lexer import *
from .parser import *

# Define the exports for this module
__all__ = ['rules, grammar']


### Definiton of token rules ###

rules = [
  # Whitespace tokens
  Rule(None, r'[ \t]+'),

  # Bracket tokens
  Rule('parenthesis_left', r'\(', None),
  Rule('parenthesis_right', r'\)', None),
  Rule('square_bracket_left', r'\[', None),
  Rule('square_bracket_right', r'\]', None),
  Rule('curly_bracket_left', r'\{', None),
  Rule('curly_bracket_right', r'\}', None),

  # Symbol tokens
  Rule('symbol_arrow', r'->', None),
  Rule('symbol_comma', r',', None),
  Rule('symbol_colon', r':', None),

  # Operator tokens
  Rule('operator_add', r'\+'),
  Rule('operator_sub', r'\-'),
  Rule('operator_mul', r'\*'),
  Rule('operator_div', r'\/'),
  Rule('operator_eq', r'=='),
  Rule('operator_neq', r'!='),
  Rule('operator_match', r'~'),
  Rule('operator_lte', r'<='),
  Rule('operator_lt', r'<'),
  Rule('operator_gte', r'>='),
  Rule('operator_gt', r'>'),
  Rule('operator_in', r'in'),
  Rule('operator_assign', r'='),

  # Keyword tokens
  Rule('keyword_or', r'or', None),
  Rule('keyword_and', r'and', None),
  Rule('keyword_not', r'not', None),
  Rule('keyword_print', r'print', None),
  Rule('keyword_var', r'var', None),
  Rule('keyword_from', r'from', None),
  #Rule('keyword_get', r'get', None),
  #Rule('keyword_set', r'set', None),
  #Rule('keyword_delete', r'delete', None),
  Rule('keyword_if', r'if', None),
  Rule('keyword_include', r'include', None),
  Rule('keyword_import', r'import', None),

  # Literal tokens
  Rule('literal_false', r'false', None),
  Rule('literal_true', r'true', None),
  Rule('literal_string', r'"((?:[^"\\]|\\.)*)"', 1),
  Rule('literal_date', r'\d{4}-\d{2}-\d{2}'),
  Rule('literal_int', r'\-?(?:0|[1-9][0-9]*)'),
  Rule('literal_float', r'\-?(?:0|[1-9][0-9]*)\.[0-9]+'),

  # Variable name tokens
  Rule('identifier', r'[A-Za-z_][A-Za-z0-9_]*')
]


### Definiton of parser rules ###

# Return a parser between parentheses
def parenthesized(parser):
  return parser.between(token('parenthesis_left'), token('parenthesis_right'))

# Return a parser between square brackets
def square_bracketed(parser):
  return parser.between(token('square_bracket_left'), token('square_bracket_right'))

# Return a parser between square brackets
def curly_bracketed(parser):
  return parser.between(token('curly_bracket_left'), token('curly_bracket_right'))

# Literals
literal_false = token('literal_false').value(internals.ObjBool(False))
literal_true = token('literal_true').value(internals.ObjBool(True))
literal_int = token('literal_int').map(internals.ObjInt)
literal_float = token('literal_float').map(internals.ObjFloat)
literal_string = token('literal_string').map(internals.ObjString)
literal_regex = token('identifier', 'regex') >> token('literal_string').map(internals.ObjRegex)
literal_date = token('literal_date').map(internals.ObjDate)
literal = (literal_false | literal_true | literal_int | literal_float | literal_string | literal_regex | literal_date).map(ast.LiteralExpr)

# List primitives
list_parameter = lazy(lambda: expr)
list_base = list_parameter.many_separated(token('symbol_comma')).map(ast.ListExpr)
list = square_bracketed(list_base)

# Record primitives
record_parameter = concat(token('identifier'), token('symbol_colon') >> lazy(lambda: expr), lambda name, value: (name, value))
record_base = record_parameter.many_separated(token('symbol_comma')).map(ast.RecordExpr)
record = curly_bracketed(record_base)

# Primitives
primitive = literal | list | record

# Helper parsers
parameters = token('identifier').many_separated(token('symbol_comma'))
arguments = lazy(lambda: expr).many_separated(token('symbol_comma'))

# Primitive expressions
variable = token('identifier').map(ast.VariableExpr)
primary = primitive | variable | parenthesized(lazy(lambda: expr))
call = concat(primary, parenthesized(lazy(lambda: arguments)), ast.CallExpr) | primary

# Arithmetic expressions
multiplication_op = token('operator_mul') | token('operator_div')
multiplication = call.reduce_separated(multiplication_op, ast.BinaryOpExpr, min = 1, parse_separator = True)
addition_op = token('operator_add') | token('operator_sub')
addition = multiplication.reduce_separated(addition_op, ast.BinaryOpExpr, min = 1, parse_separator = True)

# Comparison expressions
comparison_op = token('operator_lt') | token('operator_lte') | token('operator_gt') | token('operator_gte') | token('operator_match') | token('operator_in')
comparison = concat_multiple(ast.BinaryOpExpr, addition, comparison_op, addition) | addition

# Equality expressions
equality_op = token('operator_eq') | token('operator_neq')
equality = concat_multiple(ast.BinaryOpExpr, comparison, equality_op, comparison) | comparison

# Logic expressions
logic_not = token('keyword_not') >> lazy(lambda: logic_not).map(lambda expr: ast.UnaryOpExpr('not', expr)) | equality
logic_and = logic_not.reduce_separated(token('keyword_and'), lambda l, r: ast.BinaryOpExpr(l, 'and', r), min = 1)
logic_or = logic_and.reduce_separated(token('keyword_or'), lambda l, r: ast.BinaryOpExpr(l, 'or', r), min = 1)

# Query expressions
query_get_action = token('identifier', 'get') >> lazy(lambda: expr).optional(None).map(lambda expr: ('get', expr))
query_set_action = token('identifier', 'set') >> lazy(lambda: expr).map(lambda expr: ('set', expr))
query_delete_action = token('identifier', 'delete').value(('delete', None))
query_action = query_get_action | query_set_action | query_delete_action
query_where = token('keyword_if') >> lazy(lambda: expr)
query = token('keyword_from') >> concat_multiple(ast.QueryExpr, logic_or, query_action, query_where.optional()) | logic_or

# Assignment expressions
assignment_op = token('operator_assign')
assignment = concat(token('identifier'), assignment_op >> lazy(lambda: assignment), ast.AssignmentExpr) | query

# Expressions
expr = assignment

# Arguments
argument = concat(token('identifier'), token('symbol_colon').then(expr).optional(internals.ObjBool(True)), lambda key, value: (key, value))
argument_list = argument.many_separated(token('symbol_comma')).map(dict)

# Statements
expr_stmt = expr.map(ast.ExprStmt)
print_stmt = token('keyword_print') >> concat(expr, (token('symbol_comma') >> record_base).optional(ast.RecordExpr()), ast.PrintStmt)
variable_stmt = token('keyword_var') >> concat(token('identifier'), token('operator_assign').then(expr).optional(), ast.VariableStmt)
include_stmt = token('keyword_include') >> literal_string.map(ast.IncludeStmt)
import_stmt = token('keyword_import') >> concat(expr, (token('symbol_comma') >> record_base).optional(ast.RecordExpr()), ast.ImportStmt)
stmt = expr_stmt | print_stmt | variable_stmt | include_stmt | import_stmt

# Statement lists
stmt_list = stmt.many_separated(token('newline')).map(ast.BlockStmt)

# Grammar
grammar = stmt_list.phrase()
