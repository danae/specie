from . import ast, internals, parser


### Definiton of token rules ###

# List of token rules
rules = [
  # Whitespace tokens
  parser.Rule('whitespace', r'[ \t]+', ignore = True),

  # Bracket tokens
  parser.Rule('parenthesis_left', r'\(', None),
  parser.Rule('parenthesis_right', r'\)', None),
  parser.Rule('square_bracket_left', r'\[', None),
  parser.Rule('square_bracket_right', r'\]', None),
  parser.Rule('curly_bracket_left', r'\{', None),
  parser.Rule('curly_bracket_right', r'\}', None),

  # Symbol tokens
  parser.Rule('symbol_dot', r'\.', None),
  parser.Rule('symbol_comma', r'\,', None),
  parser.Rule('symbol_colon', r'\:', None),
  parser.Rule('symbol_arrow', r'->', None),

  # Operator tokens
  parser.Rule('operator_add', r'\+'),
  parser.Rule('operator_sub', r'\-'),
  parser.Rule('operator_mul', r'\*'),
  parser.Rule('operator_div', r'\/'),
  parser.Rule('operator_eq', r'=='),
  parser.Rule('operator_neq', r'!='),
  parser.Rule('operator_match', r'~'),
  parser.Rule('operator_lte', r'<='),
  parser.Rule('operator_lt', r'<'),
  parser.Rule('operator_gte', r'>='),
  parser.Rule('operator_gt', r'>'),
  parser.Rule('operator_in', r'in'),
  parser.Rule('operator_or', r'or'),
  parser.Rule('operator_and', r'and'),
  parser.Rule('operator_not', r'not'),
  parser.Rule('operator_assign', r'='),

  # Keyword tokens
  parser.Rule('keyword_do', r'do', None),
  parser.Rule('keyword_if', r'if', None),
  parser.Rule('keyword_end', r'end', None),
  parser.Rule('keyword_from', r'from', None),
  parser.Rule('keyword_regex', r'regex', None),
  parser.Rule('keyword_var', r'var', None),

  # Literal tokens
  parser.Rule('literal_false', r'false', None),
  parser.Rule('literal_true', r'true', None),
  parser.Rule('literal_string', r'"((?:[^"\\]|\\.)*)"', 1),
  parser.Rule('literal_date', r'\d{4}-\d{2}-\d{2}'),
  parser.Rule('literal_int', r'\-?(?:0|[1-9][0-9]*)'),
  parser.Rule('literal_float', r'\-?(?:0|[1-9][0-9]*)\.[0-9]+'),

  # Variable name tokens
  parser.Rule('identifier', r'[A-Za-z_][A-Za-z0-9_]*')
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
      raise parser.ParserError(None, "A keyword argument cannot be followed by a positional argument")

  # Return the lists as the appropriate expressions
  return ast.Arguments(ast.ListExpr(args), ast.RecordExpr(kwargs))

# Map a call expression
def map_call(expr, token, value):
  # Check if the token is a left parenthesis
  if token.name == 'parenthesis_left':
    return ast.CallExpr(expr, token, value)

  # Check if the token is a dot
  elif token.name == 'symbol_dot':
    return ast.GetExpr(expr, token, value)

  # Otherwise fail
  raise parser.ParserError(f"Invalid token in call expression: {token}")

# Map an assignment expression
def map_assignment(expr, op, value):
  # Check if the expression is a variable expression
  if isinstance(expr, ast.VariableExpr):
    return ast.AssignmentExpr(expr.name, op, value)

  # Check if the expression is a get expression
  elif isinstance(expr, ast.GetExpr):
    return ast.SetExpr(expr.expression, expr.token, expr.name, op, value)

  # Otherwise fail
  raise parser.ParserError(f"Invalid assignment target: {expr.token}")


### Definiton of parser rules ###

# Register all token parsers in the global dictionary for easier access
for rule in rules:
  globals()[rule.name.upper()] = parser.describe(rule.name.upper(), parser.token(rule.name))


# Parse a parser between parentheses
def parenthesized(p):
  return parser.between(p, PARENTHESIS_LEFT, PARENTHESIS_RIGHT)

# Parse a parser between square brackets
def square_bracketed(p):
  return parser.between(p, SQUARE_BRACKET_LEFT, SQUARE_BRACKET_RIGHT)

# Parse a parser between curly brackets
def curly_bracketed(p):
  return parser.between(p, CURLY_BRACKET_LEFT, CURLY_BRACKET_RIGHT)

# Literals
literal_false = parser.describe('literal_false', parser.map_value(internals.ObjBool(False), LITERAL_FALSE))
literal_true = parser.describe('literal_true', parser.map_value(internals.ObjBool(True), LITERAL_TRUE))
literal_int = parser.describe('literal_int', parser.map(lambda t: internals.ObjInt(t.value), LITERAL_INT))
literal_float = parser.describe('literal_float', parser.map(lambda t: internals.ObjFloat(t.value), LITERAL_FLOAT))
literal_string = parser.describe('literal_string', parser.map(lambda t: internals.ObjString(t.value), LITERAL_STRING))
literal_regex = parser.describe('literal_regex', parser.map(lambda t: internals.ObjRegex(t.value), KEYWORD_REGEX >> LITERAL_STRING))
literal_date = parser.describe('literal_date', parser.map(lambda t: internals.ObjDate(t.value), LITERAL_DATE))
literal = parser.describe('literal', parser.map(ast.LiteralExpr, literal_false | literal_true | literal_int | literal_float | literal_string | literal_regex | literal_date))

# List primitives
list_item = parser.describe('list_item', parser.lazy(lambda: expr))
list = parser.describe('list', parser.map(ast.ListExpr, square_bracketed(list_item * SYMBOL_COMMA)))

# Record primitives
record_item = parser.describe('record_item', IDENTIFIER + (SYMBOL_COLON >> parser.lazy(lambda: expr)))
record = parser.describe('record', parser.map(ast.RecordExpr, curly_bracketed(record_item * SYMBOL_COMMA)))

# Primary expressions
primary_variable = parser.describe('primary_variable', parser.map(ast.VariableExpr, IDENTIFIER))
primary_grouping = parser.describe('primary_grouping', parser.map(ast.GroupingExpr, parenthesized(parser.lazy(lambda: expr))))
primary = parser.describe('primary', literal | list | record | primary_variable | primary_grouping)

# Arguments
arguments_item = parser.describe('arguments_item', record_item | list_item)
arguments = parser.describe('arguments', parser.map(map_arguments, (arguments_item * SYMBOL_COMMA) ^ []))

# Call expressions
call = parser.describe('call', parser.reduce(map_call, (PARENTHESIS_LEFT + arguments << PARENTHESIS_RIGHT) | (SYMBOL_DOT + IDENTIFIER), primary))

# Arithmetic expressions
multiplication_op = parser.describe('multiplication_op', OPERATOR_MUL | OPERATOR_DIV)
multiplication = parser.describe('multiplication', parser.reduce(ast.BinaryOpExpr, multiplication_op + call, call))
addition_op = parser.describe('addition_op', OPERATOR_ADD | OPERATOR_SUB)
addition = parser.describe('addition', parser.reduce(ast.BinaryOpExpr, addition_op + multiplication, multiplication))

# Comparison expressions
comparison_op = parser.describe('comparison_op', OPERATOR_LT | OPERATOR_LTE | OPERATOR_GT | OPERATOR_GTE | OPERATOR_MATCH | OPERATOR_IN)
comparison = parser.describe('comparison', parser.concat(ast.BinaryOpExpr, addition, comparison_op, addition) | addition)

# Equality expressions
equality_op = parser.describe('equality_op', OPERATOR_EQ | OPERATOR_NEQ)
equality = parser.describe('equality', parser.concat(ast.BinaryOpExpr, comparison, equality_op, comparison) | comparison)

# Logic expressions
logic_not = parser.describe('logic_not', parser.concat(ast.UnaryOpExpr, OPERATOR_NOT, parser.lazy(lambda: logic_not)) | equality)
logic_and = parser.describe('logic_and', parser.reduce(ast.LogicalExpr, OPERATOR_AND + logic_not, logic_not))
logic_or = parser.describe('logic_or', parser.reduce(ast.LogicalExpr, OPERATOR_OR + logic_and, logic_and))

# Query expressions
query_action = parser.describe('query_action', parser.concat(ast.Call, IDENTIFIER, arguments))
query_where = parser.describe('query_where', KEYWORD_IF >> parser.lazy(lambda: expr))
query = parser.describe('query', parser.concat(ast.QueryExpr, parser.map(ast.VariableExpr, KEYWORD_FROM >> IDENTIFIER), query_action, query_where ^ None) | logic_or)

# Block expressions
block_contents = parser.describe('block_contents', parser.map(ast.BlockExpr, parser.lazy(lambda: expr) * parser.token('newline')))
block_base = parser.describe('block_base', KEYWORD_DO >> parser.token('newline') >> block_contents << parser.token('newline') << KEYWORD_END)
block = parser.describe('block', block_base | query)

# Parameters
parameters_arg = parser.describe('parameters_arg', IDENTIFIER)
parameters = parser.describe('parameters', parameters_arg * SYMBOL_COMMA)

# Function expressions
function_parameters = parser.describe('function_parameters', parenthesized(parameters) | parser.map(lambda param: [param], parameters_arg))
function_body = parser.describe('function_body', SYMBOL_ARROW >> parser.lazy(lambda: expr) | block_base)
function = parser.describe('function', parser.concat(ast.FunctionExpr, function_parameters, function_body) | block)

# Assignment expressions
assignment_op = parser.describe('assignment_op', OPERATOR_ASSIGN)
assignment = parser.describe('assignment', parser.concat(map_assignment, call, assignment_op, parser.lazy(lambda: assignment)) | function)

# Declaration expressions
declaration_op = parser.describe('declaration_op', OPERATOR_ASSIGN)
declaration = parser.describe('declaration', parser.concat(ast.DeclarationExpr, KEYWORD_VAR >> IDENTIFIER, declaration_op, function) | assignment)

# Expressions
expr = parser.describe('expr', parser.synchronize(declaration, 'newline'))

# Modules
module = parser.describe('module', parser.map(ast.ModuleExpr, expr * parser.token('newline')))


# Parse an input string to an abstract syntax tree
def parse(string, is_module = True):
  # Create the lexer
  lexer = parser.Lexer(rules, comment_inline = '#', comment_block = ('#-', '-#'), comment_ignore_pattern = r'"((?:[^"\\]|\\.)*)"')

  # Parse the inout string to a list of tokens
  tokens = lexer.tokenize(string)

  # Parse the list of tokens to an abstract syntax tree
  if is_module:
    result = module.parse_strict(tokens, 0)
  else:
    result = expr.parse_strict(tokens, 0)

  # Check the result
  if result:
    return result.value
  else:
    for err in result.errors:
      print(err)
    return None