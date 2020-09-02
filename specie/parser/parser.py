import functools

# Define the exports for this module
__all__ = [
  'empty', 'token', 'lazy', 'map', 'value', 'concat', 'then', 'before',
  'between', 'concat_multiple', 'alternate', 'optional', 'many',
  'many_separated', 'many_separated_and_terminated',
  'many_separated_and_optionally_terminated', 'phrase', 'lazy',
  'ParserError', 'UnexpectedEndOfTokens', 'UnexpectedToken'
]


# Wrap a parser to print its result
debug_indent = 0
def debug(parser_class):
  global debug_indent

  original_call = parser_class.parse
  def parse(self, tokens, index):
    global debug_indent

    self_repr = repr(self)
    self_repr = (self_repr[:100] + "...") if len(self_repr) > 100 else self_repr
    print("|   " * debug_indent + "{}:".format(self_repr))

    debug_indent += 1
    try:
      result = original_call(self, tokens, index)
      debug_indent -= 1
      print("|   " * debug_indent + "|-> \033[32m{!s}\033[39m".format(result))
      return result
    except ParserError as e:
      debug_indent -= 1
      print("|   " * debug_indent + "|-> \033[31m{!s}\033[39m".format(e))
      raise


  parser_class.parse = parse
  return parser_class


### Definition of the parser class ###

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
    return self.description or f"{self.__class__.__name__}({self.function})"

  # Definition of object oriented versions of the parser functions
  def map(self, function):
    return map(self, function)

  def value(self, val):
    return value(self, val)

  def concat(self, other, function):
    return concat(self, other, function)

  def then(self, after):
    return then(self, after)

  def before(self, before):
    return before(before, self)

  def between(self, before, after = None):
    return between(self, before, after)

  def alternate(self, other):
    return alternate(self, other)

  def optional(self, default = None):
    return optional(self, default)

  def many(self, *, min = 0, max = 0):
    return many(self, map=map, min=min, max=max)

  def many_separated(self, separator, *, min = 0, max = 0, parse_separator = False):
    return many_separated(self, separator, min=min, max=max, parse_separator=parse_separator)

  def many_separated_and_terminated(self, separator, *, min = 0, max = 0, parse_separator = False):
    return many_separated_and_terminated(self, separator, min=min, max=max, parse_separator=parse_separator)

  def many_separated_and_optionally_terminated(self, separator, *, min = 0, max = 0, parse_separator = False):
    return many_separated_and_optionally_terminated(self, separator, min=min, max=max, parse_separator=parse_separator)

  def reduce(self, function, initializer = None, *, min = 0, max = 0):
    return reduce(self, function, initializer, map=map, min=min, max=max)

  def reduce_separated(self, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False):
    return reduce_separated(self, separator, function, initializer, min=min, max=max, parse_separator=parse_separator)

  def reduce_separated_and_terminated(self, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False):
    return reduce_separated_and_terminated(self, separator, function, initializer, min=min, max=max, parse_separator=parse_separator)

  def reduce_separated_and_optionally_terminated(self, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False):
    return reduce_separated_and_optionally_terminated(self, separator, function, initializer, min=min, max=max, parse_separator=parse_separator)

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

# Return an empty parser
def empty(*, description = None):
  @parser_function(description = description or f"empty()")
  def parse_empty(tokens, index):
    return ParseResult(None, index)
  return parse_empty

# Return a parser with the value of the parsed token
def token(name, *, description = None):
  @parser_function(description = description or f"token({name})")
  def parse_token(tokens, index):
    if index == len(tokens):
      raise UnexpectedEndOfTokens(index)
    else:
      token = tokens[index]
      if token.name == name:
        return ParseResult(token.value, index + 1)
      else:
        raise UnexpectedToken(token)
  return parse_token

# Return a parser that lazily evaluates the parser factory upon parsing
def lazy(parser_factory, *, description = None):
  @parser_function(description = description or f"lazy({parser_factory})")
  def parse_lazy(tokens, index):
    return parser_factory().parse(tokens, index)
  return parse_lazy

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
  function = function or (lambda l, r: (l, r))

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
      return ParseResult(default, index) if not result else result
    except ParserError:
      return ParseResult(default, index)
  return parse_optional

# Return the result of multiple identical parsers
# min must be at least 0; max must be at least 1, or 0 for no maximum
def many(parser, separator = empty(), terminator = empty(), *, min = 0, max = 0, parse_separator = False, description = None):
  @parser_function(description = description or f"many({parser}, {separator}, {terminator}, {min=}, {max=}, {parse_separator=})")
  def parse_many(tokens, index):
    results = []

    # Parse the first occurence
    result = parser.parse(tokens, index)
    result.value = (None, result.value)
    while result:
      # Append the result to the list
      if not parse_separator:
        result.value = result.value[1]
      results.append(result.value)
      index = result.index

      if max > 0 and len(results) == max:
        break

      # Parse the next occurence
      try:
        result = concat(separator, parser, lambda s, p: (s, p)).parse(tokens, index)
      except ParserError:
        break

    # Terminate and return
    if len(results) >= min and terminator.parse(tokens, index):
      return ParseResult(results, index)
    #elif index >= len(tokens):
    #  raise UnexpectedEndOfTokens(index)
    else:
      raise UnexpectedToken(tokens[index])
  return parse_many

# Return the result of multiple identical parsers separated by another parser
def many_separated(parser, separator, *, min = 0, max = 0, parse_separator = False, description = None):
  return many(parser, separator, min=min, max=max, parse_separator=parse_separator,
    description = description or f"many_separated({parser}, {separator}, {min=}, {max=}, {parse_separator=})")

# Return the result of multiple identical parsers separated and terminated by another parser
def many_separated_and_terminated(parser, separator, *, min = 0, max = 0, parse_separator = False, description = None):
  return many(parser, separator, separator, min=min, max=max, parse_separator=parse_separator,
    description = description or f"many_separated_and_terminated({parser}, {separator}, {min=}, {max=}, {parse_separator=})")

# Return the result of multiple identical parsers separated and optionally terminated by another parser
def many_separated_and_optionally_terminated(parser, separator, *, min = 0, parse_separator = False, max = 0, description = None):
  return many(parser, separator, optional(separator), min=min, max=max, parse_separator=parse_separator,
    description = description or f"many_separated_and_optionally_terminated({parser}, {separator}, {min=}, {max=}, {parse_separator=})")

# Return a parser that reduces multiple identical parsers into a single result
def reduce(parser, function, initializer = None, separator = empty(), terminator = empty(), *, min = 0, max = 0, parse_separator = False, description = None):
  @parser_function(description = description or f"reduce({function}, {parser}, {min=}, {max=})")
  def parse_reduce(tokens, index):
    result = many(parser, separator, terminator, min=min, max=max, parse_separator=parse_separator).parse(tokens, index)
    if not result.value:
      return result
    elif parse_separator:
      return ParseResult(functools.reduce(lambda a, i: function(a, *i), result.value[1:], result.value[0][1]), result.index)
    elif initializer is not None:
      return ParseResult(functools.reduce(function, result.value, initializer), result.index)
    else:
      return ParseResult(functools.reduce(function, result.value), result.index)
  return parse_reduce

# Return a parser that reduces multiple identical parsers separated by another parser into a single result
def reduce_separated(parser, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False, description = None):
  return reduce(parser, function, initializer, separator, min=min, max=max, parse_separator=parse_separator,
    description = description or f"reduce_separated({function}, {parser}, {min=}, {max=}, {parse_separator=})")

# Return a parser that reduces multiple identical parsers separated by another parser into a single result
def reduce_separated_and_terminated(parser, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False, description = None):
  return reduce(parser, function, initializer, separator, separator, min=min, max=max, parse_separator=parse_separator,
    description = description or f"reduce_separated_and_terminated({function}, {parser}, {min=}, {max=}, {parse_separator=})")

# Return a parser that reduces multiple identical parsers separated by another parser into a single result
def reduce_separated_and_optionally_terminated(parser, separator, function, initializer = None, *, min = 0, max = 0, parse_separator = False, description = None):
  return reduce(parser, function, initializer, separator, optional(separator), min=min, max=max, parse_separator=parse_separator,
    description = description or f"reduce_separated_and_optionally_terminated({function}, {parser}, {min=}, {max=}, {parse_separator=})")

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
