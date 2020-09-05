from functools import reduce

from . import lexer
from .. import ast, internals

from .lexer import *
from .parser import *

# Define the exports for this module
__all__ = ['rules, grammar']


### Definiton of token rules ###

# List of token rules
rules = [
  # Whitespace tokens
  Rule('whitespace', r'[ \t]+', ignore = True),

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
  Rule('operator_or', r'or'),
  Rule('operator_and', r'and'),
  Rule('operator_not', r'not'),
  Rule('operator_assign', r'='),

  # Keyword tokens
  Rule('keyword_regex', r'regex', None),
  Rule('keyword_var', r'var', None),
  Rule('keyword_from', r'from', None),
  Rule('keyword_if', r'if', None),

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


### Definition of parser helper methods ###

# Map a list of arguments to positional and keyword arguments
def map_arguments(list):
  # Create two lists to store the arguments and keywords
  args = []; kwargs = []

  # Iterate over the arguments
  for item in list:
    if isinstance(item, tuple):
      # The call argument is a keyword argument
      kwargs.append(item)
    elif not kwargs:
      # The call argument is a positional argument
      args.append(item)
    else:
      # A positional argument was found after a keyword argument, which is invalid
      raise ParserError("A keyword argument cannot be followed by a positional argument")

  # Return the lists as the appropriate expressions
  return ast.Arguments(ast.ListExpr(args), ast.RecordExpr(kwargs))


### Definiton of parser rules ###

# Register all token parsers in the global dictionary for easier access
for rule in rules:
  globals()[rule.name.upper()] = token(rule.name)

# Literals
literal_false = LITERAL_FALSE.value(internals.ObjBool(False))
literal_true = LITERAL_TRUE.value(internals.ObjBool(True))
literal_int = LITERAL_INT.map(lambda t: internals.ObjInt(t.value))
literal_float = LITERAL_FLOAT.map(lambda t: internals.ObjFloat(t.value))
literal_string = LITERAL_STRING.map(lambda t: internals.ObjString(t.value))
literal_regex = KEYWORD_REGEX >> LITERAL_STRING.map(lambda t: internals.ObjRegex(t.value))
literal_date = LITERAL_DATE.map(lambda t: internals.ObjDate(t.value))
literal = (literal_false | literal_true | literal_int | literal_float | literal_string | literal_regex | literal_date).map(ast.LiteralExpr)

# List primitives
list_arg = lazy(lambda: expr)
list = SQUARE_BRACKET_LEFT >> list_arg.many_separated(SYMBOL_COMMA).map(ast.ListExpr) << SQUARE_BRACKET_RIGHT

# Record primitives
record_arg = concat(IDENTIFIER, SYMBOL_COLON >> lazy(lambda: expr), lambda name, value: (name, value))
record = CURLY_BRACKET_LEFT >> record_arg.many_separated(SYMBOL_COMMA).map(ast.RecordExpr) << CURLY_BRACKET_RIGHT

# Primary expressions
primary = literal | list | record | IDENTIFIER.map(ast.VariableExpr) | PARENTHESIS_LEFT >> lazy(lambda: expr).map(ast.GroupingExpr) << PARENTHESIS_RIGHT

# Arguments
arguments_arg = record_arg | list_arg
arguments = arguments_arg.many_separated(SYMBOL_COMMA).optional([]).map(map_arguments)

# Call expressions
call = concat_multiple(ast.CallExpr, primary, PARENTHESIS_LEFT, arguments << PARENTHESIS_RIGHT) | primary

# Arithmetic expressions
multiplication_op = OPERATOR_MUL | OPERATOR_DIV
multiplication = call.reduce_separated(multiplication_op, ast.BinaryOpExpr, min = 1, parse_separator = True)
addition_op = OPERATOR_ADD | OPERATOR_SUB
addition = multiplication.reduce_separated(addition_op, ast.BinaryOpExpr, min = 1, parse_separator = True)

# Comparison expressions
comparison_op = OPERATOR_LT | OPERATOR_LTE | OPERATOR_GT | OPERATOR_GTE | OPERATOR_MATCH | OPERATOR_IN
comparison = concat_multiple(ast.BinaryOpExpr, addition, comparison_op, addition) | addition

# Equality expressions
equality_op = OPERATOR_EQ | OPERATOR_NEQ
equality = concat_multiple(ast.BinaryOpExpr, comparison, equality_op, comparison) | comparison

# Logic expressions
logic_not = concat(OPERATOR_NOT, lazy(lambda: logic_not), ast.UnaryOpExpr) | equality
logic_and = logic_not.reduce_separated(OPERATOR_AND, ast.BinaryOpExpr, min = 1, parse_separator = True)
logic_or = logic_and.reduce_separated(OPERATOR_OR, ast.BinaryOpExpr, min = 1, parse_separator = True)

# Query expressions
query_action = concat(IDENTIFIER, arguments, ast.Call)
query_where = KEYWORD_IF >> lazy(lambda: expr)
query = concat_multiple(ast.QueryExpr, KEYWORD_FROM >> IDENTIFIER.map(ast.VariableExpr), query_action, query_where.optional()) | logic_or

# Assignment expressions
assignment_op = OPERATOR_ASSIGN
assignment = concat_multiple(ast.AssignmentExpr, IDENTIFIER, assignment_op, lazy(lambda: assignment)) | query

# Declaration expressions
declaration_op = OPERATOR_ASSIGN
declaration = KEYWORD_VAR >> concat_multiple(ast.DeclarationExpr, IDENTIFIER, declaration_op, query) | assignment

# Expressions
expr = declaration

# Expression lists
expr_list = expr.many_separated(token('newline')).map(lambda exprs: ast.BlockExpr(exprs, False))

# Grammar
grammar = expr_list.phrase()
