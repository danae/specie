import functools

# Define the exports for this module
__all__ = [
  'describe', 'empty', 'token', 'lazy', 'debug', 'map', 'value', 'concat',
  'then', 'before', 'between', 'concat_multiple', 'alternate', 'optional',
  'many', 'many_separated', 'many_separated_and_terminated',
  'many_separated_and_optionally_terminated', 'reduce', 'phrase',
  'ParserError', 'UnexpectedEndOfTokens', 'UnexpectedToken'
]


### Definition of the parser class ###

# Return a wrapped parser that prints its result for debugging purposes
debug_indent = 0
def debug(parser):
  parse = parser.parse

  def debug_wrapper(self, tokens, index):
    global debug_indent

    parser_repr = repr(self)
    parser_repr = (parser_repr[:100] + "...") if len(parser_repr) > 100 else parser_repr
    #print("| " * debug_indent + "{}:".format(parser_repr))

    debug_indent += 1
    try:
      result = parse(self, tokens, index)
      debug_indent -= 1
      print("-" * debug_indent + " {}:".format(parser_repr))
      print("-" * debug_indent + " \033[32m{!s}\033[39m".format(result))
      return result
    except ParserError as e:
      debug_indent -= 1
      print("-" * debug_indent + " {}:".format(parser_repr))
      print("-" * debug_indent + " \033[31m{!s}\033[39m".format(e))
      raise

  parser.parse = debug_wrapper
  return parser

# Class that defines a parser
class Parser():
  # Constructor
  def __init__(self, func = None, description = None):
    self.func = func
    self.description = description

  # Parse a stream of tokens at the specified index
  def parse(self, tokens, index):
    return self.func(tokens, index)

  # Convert to string representation
  def __repr__(self):
    return self.description or f"{self.__class__.__name__}({self.func})"

  # Definition of object oriented versions of the parser functions
  def map(self, function):
    return map(self, function)

  def value(self, val):
    return value(self, val)

  def concat(self, other, function):
    return concat(self, other, function)

  def then(self, right):
    return then(self, right)

  def before(self, right):
    return before(self, right)

  def between(self, left, right = None):
    return between(self, left, right)

  def alternate(self, other):
    return alternate(self, other)

  def optional(self, default = None):
    return optional(self, default)

  def many(self, *, min = 0, max = 0):
    return many(self, map=map, min=min, max=max)

  def many_separated(self, separator, *, min = 0, max = 0):
    return many_separated(self, separator, min=min, max=max)

  def many_separated_and_terminated(self, separator, *, min = 0, max = 0):
    return many_separated_and_terminated(self, separator, min=min, max=max)

  def many_separated_and_optionally_terminated(self, separator, *, min = 0, max = 0):
    return many_separated_and_optionally_terminated(self, separator, min=min, max=max)

  def reduce(self, function, *iterator, min = 0, max = 0):
    return reduce(self, function, *iterator, min=min, max=max)

  def phrase(self):
    return phrase(self)

  # Operator overloading (>>) for then parser
  def __rshift__(self, after):
    return self.then(after)

  # Operator overloading (<<) for before parser
  def __lshift__(self, before):
    return self.before(before)

  # Operator overloading (|) for alternate parser
  def __or__(self, parser):
    return self.alternate(parser)


### Definition of parser functions ###

# Return a parser with the parser result returned by the function
def parser_function(*, description = None):
  return lambda func: Parser(func, description)

# Return the parser but with the specified description
def describe(description, parser):
  parser.description = description
  return parser

# Return an empty parser
def empty(*, description = None):
  @parser_function(description = description or f"empty()")
  def parse_empty(tokens, index):
    return ParseResult(None, index)
  return parse_empty

# Return a parser with the value of the parsed token
def token(name, value = None, *, description = None):
  @parser_function(description = description or f"token({name})")
  def parse_token(tokens, index):
    if index == len(tokens):
      raise UnexpectedEndOfTokens(index)
    else:
      token = tokens[index]
      if token.name == name and (value is None or token.value == value):
        return ParseResult(token, index + 1)
      else:
        raise UnexpectedToken(token)
  return parse_token

# Return a parser that lazily evaluates the parser factory upon parsing
def lazy(parser_factory, *, description = None):
  @parser_function(description = description or f"lazy({parser_factory})")
  def parse_lazy(tokens, index):
    return parser_factory().parse(tokens, index)
  return parse_lazy


### Definition of parser combinators ###

# Return a parser that maps the result using the specified function
def map(parser, function, *, description = None):
  @parser_function(description = description or f"map({parser}, {function})")
  def parse_map(tokens, index):
    result = parser.parse(tokens, index)
    return ParseResult(function(result.value), result.index)
  return parse_map

# Return a parser with the specified value as the result
def value(parser, val, *, description = None):
  @parser_function(description = description or f"value({parser}, {val})")
  def parse_value(tokens, index):
    return map(parser, lambda _: val).parse(tokens, index)
  return parse_value

# Return a parser that concatenates two parses using the specified function
def concat(left, right, function, *, description = None):
  @parser_function(description = description or f"concat({left}, {right}, {function})")
  def parse_concat(tokens, index):
    left_result = left.parse(tokens, index)
    right_result = right.parse(tokens, left_result.index)
    return ParseResult(function(left_result.value, right_result.value), right_result.index)
  return parse_concat

# Return a concat parser for a list of parsers
def concat_multiple(function, *parsers):
  if len(parsers) <= 1:
    raise ValueError("parsers must at least contain one element")

  parsers = list(parsers)
  map_parser = parsers.pop(0)
  for parser in parsers:
    map_parser = concat(map_parser, parser, lambda left, right: (*left, right) if isinstance(left, tuple) else (left, right))
  return map_parser.map(lambda args: function(*args))

# Return a parser that returns the result of the second parser
def then(left, right, *, description = None):
  return concat(left, right, lambda _, result: result,
    description = description or f"then({left}, {right})")

# Return a parser that returns the result of the first parser
def before(left, right, *, description = None):
  return concat(left, right, lambda result, _: result,
    description = description or f"before({left}, {right})")

# Return a parser that returns the result of the parser between the specified parsers
def between(parser, left, right = None, *, description = None):
  right = right or left
  return then(left, before(parser, right),
    description = description or f"between({parser}, {left}, {right})")

# Return a parser with the result of the left parser, or the result of the right parser if the left parser fails
def alternate(left, right, *, description = None):
  @parser_function(description = description or f"alternate({left}, {right})")
  def parse_alternate(tokens, index):
    try:
      left_result = left.parse(tokens, index)
      if left_result:
        return left_result
    except ParserError:
      pass
    return right.parse(tokens, index)
  return parse_alternate

# Return a parser with a default result value if the parser fails
def optional(parser, default = None, *, description = None):
  @parser_function(description = description or f"optional({parser}, {default})")
  def parse_optional(tokens, index):
    try:
      result = parser.parse(tokens, index)
      return ParseResult(default, index) if result is None else result
    except ParserError:
      return ParseResult(default, index)
  return parse_optional

# Return the result of multiple identical parsers
# min must be at least 0; max must be at least 1, or 0 for no maximum
def many(parser, separator = empty(), terminator = empty(), *, min = 0, max = 0, description = None):
  @parser_function(description = description or f"many({parser}, {separator}, {terminator}, {min=}, {max=})")
  def parse_many(tokens, index):
    results = []

    # Parse the first occurence
    try:
      result = parser.parse(tokens, index)
      while result:
        # Append the result to the list
        results.append(result.value)
        index = result.index

        # Parse the next occurence
        result = then(separator, parser).parse(tokens, index)
    except ParserError:
      pass

    # Terminate and return
    if min <= len(results) and (max == 0 or max >= len(results)) and terminator.parse(tokens, index):
      return ParseResult(results, index)
    else:
      raise UnexpectedToken(tokens[index])
  return parse_many

# Return the result of multiple identical parsers separated by another parser
def many_separated(parser, separator, *, min = 0, max = 0, description = None):
  return many(parser, separator, min=min, max=max,
    description = description or f"many_separated({parser}, {separator}, {min=}, {max=})")

# Return the result of multiple identical parsers separated and terminated by another parser
def many_separated_and_terminated(parser, separator, *, min = 0, max = 0, description = None):
  return many(parser, separator, separator, min=min, max=max,
    description = description or f"many_separated_and_terminated({parser}, {separator}, {min=}, {max=})")

# Return the result of multiple identical parsers separated and optionally terminated by another parser
def many_separated_and_optionally_terminated(parser, separator, *, min = 0, max = 0, description = None):
  return many(parser, separator, optional(separator), min=min, max=max,
    description = description or f"many_separated_and_optionally_terminated({parser}, {separator}, {min=}, {max=})")

# Return a parser that reduces an iterator of parsers using the specified function and the initializer
def reduce(initializer, function, *iterator, min = 0, max = 0, description = None):
  @parser_function(description = description or f"reduce({initializer}, {function}, {', '.join(str(e) for e in iterator)}, {min=}, {max=})")
  def parse_reduce(tokens, index):
    # Parse the initializer
    initializer_result = initializer.parse(tokens, index)
    if initializer_result.value is None:
      return initializer_result

    # Parse the iterator
    iterator_result = many(concat_multiple(lambda *args: tuple(args), *iterator), min = min, max = max).parse(tokens, initializer_result.index)
    if iterator_result.value is None:
      return iterator_result

    # Reduce the iterator
    value = initializer_result.value
    for element in iterator_result.value:
      value = function(value, *element)

    # Return the value
    return ParseResult(value, iterator_result.index)
  return parse_reduce

# Return a parser if that parser consumed all tokens
def phrase(parser, *, description = None):
  @parser_function(description = description or f"phrase({parser})")
  def parse_phrase(tokens, index):
    result = parser.parse(tokens, index)
    if result and result.index == len(tokens):
      return result
    else:
      raise UnexpectedToken(tokens[result.index])
  return parse_phrase


### Definiton of the parser result ###

# Class that defines a parser result
class ParseResult:
  def __init__(self, value, index):
    self.value = value
    self.index = index

  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r}, {self.index!r})"

  def __str__(self):
    return f"{type(self.value).__name__}({self.value}) at index {self.index}"


### Definition of parser errors ###

# Parse error class
class ParserError(RuntimeError):
  def __init__(self, message):
    self.message = message

  def __repr__(self):
    return f"{self.__class__.__name__}({self.message})"

  def __str__(self):
    return self.message


# Error that is raised when the end of the token stream is reached
class UnexpectedEndOfTokens(ParserError):
  def __init__(self, index):
    self.index = index
    self.message = f"Unexpected end of tokens at index {self.index}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.index})"

  def __str__(self):
    return self.message


# Error that is raised when an unexpected token is reached
class UnexpectedToken(ParserError):
  def __init__(self, token):
    self.token = token
    self.message = f"Unexpected {self.token}"

  def __repr__(self):
    return f"{self.__class__.__name__}({self.token})"

  def __str__(self):
    return self.message
