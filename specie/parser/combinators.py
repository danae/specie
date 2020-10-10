import functools

from .parser import Parser, ParserResult, ParserError


# Class that defines a parser combinator
class ParserCombinator(Parser):
  # a + b -> combine(a, b)
  def __add__(self, other):
    return combine(self, other)

  # a >> b -> then(a, nofail(b))
  def __rshift__(self, other):
    return then(self, nofail(other))

  # a << b -> before(a, nofail(b))
  def __lshift__(self, other):
    return before(self, nofail(other))

  # a | b -> alternate(a, b)
  def __or__(self, other):
    return alternate(self, other)

  # a ^ default -> optional(a, default)
  def __xor__(self, default):
    return optional(self, default)

  # a * separator -> many_sep(a, separator)
  def __mul__(self, separator):
    return many_sep(self, separator)


### Definition of parser result functions ###

# Return the next token if it matches the specified name and advance
def token(name):
  @functools.wraps(token)
  def parse_token(tokens, index):
    # Check if there are tokens left to consume
    if index >= len(tokens):
      return ParserError.unexpected(tokens, index)

    # Check the type of the token
    if tokens[index].name == name:
      return ParserResult(tokens[index], index + 1)
    else:
      return ParserError.unexpected(tokens, index, name)
  return ParserCombinator(parse_token)


# Return an empty result
def empty():
  @functools.wraps(empty)
  def parse_empty(tokens, index):
    return ParserResult(None, index)
  return ParserCombinator(parse_empty)


# Return the result of the lazy evaluation of the parser factory
def lazy(parser_factory):
  @functools.wraps(lazy)
  def parse_lazy(tokens, index):
    return parser_factory().parse(tokens, index)
  return ParserCombinator(parse_lazy)


# Synchronize a parser after raising an error
def synchronize(parser, *sync_tokens):
  return parser
  #return ParserCombinator(parser.function, sync_tokens)


def nofail(parser):
  @functools.wraps(nofail)
  def parse_nofail(tokens, index):
    result = parser.parse(tokens, index)
    if result:
      return result
    else:
      raise result.errors[-1]
  return ParserCombinator(parse_nofail)


### Definition of parser combinator functions ###

# Describe a parser
describe_debug = False
describe_indent = 1
def describe(label, parser):
  if describe_debug:
    @functools.wraps(describe)
    def describe_wrapper(tokens, index):
      global describe_indent

      parser_repr = label or repr(parser)
      parser_repr = (parser_repr[:100] + "...") if len(parser_repr) > 100 else parser_repr

      print(". " * describe_indent + f"{parser_repr}")

      describe_indent += 1
      result = parser.parse(tokens, index)
      describe_indent -= 1

      if result:
        print(". " * describe_indent + f"{parser_repr}: \033[32m{result}\033[39m")
      else:
        print(". " * describe_indent + f"{parser_repr}: \033[31m{result.errors[-1]}\033[39m")

      return result
    return ParserCombinator(describe_wrapper)
  else:
    return parser


# Return a parser that maps the result using the specified function
def map(function, parser):
  @functools.wraps(map)
  def parse_map(tokens, index):
    result = parser.parse(tokens, index)
    if result:
      return ParserResult(function(result.value), result.index, result.errors)
    else:
      return result
  return ParserCombinator(parse_map)

def map_value(value, parser):
  @functools.wraps(map_value)
  def parse_map_value(tokens, index):
    result = parser.parse(tokens, index)
    return ParserResult(value, result.index, result.errors)
  return ParserCombinator(parse_map_value)


# Return the concatenated result of the specified parsers
def concat(function, *parsers):
  # If no parsers are specified, then raise an error
  if len(parsers) == 0:
    raise ValueError("parsers must at least contain one item")

  # If one parser is specified, then return its result
  elif len(parsers) == 1:
    return next(iter(parsers))

  # If two parsers are specified, then concatenate them
  elif len(parsers) == 2:
    @functools.wraps(concat)
    def parse_concat(tokens, index):
      parsers_it = iter(parsers)

      left_result = next(parsers_it).parse(tokens, index)
      if not left_result:
        return left_result

      right_result = next(parsers_it).parse(tokens, left_result.index)
      if not right_result:
        return right_result

      return ParserResult(function(left_result.value, right_result.value), right_result.index)
    return ParserCombinator(parse_concat)

  # If more parsers are specified, then recursively concatenate them
  else:
    @functools.wraps(concat)
    def parse_concat_more(tokens, index):
      parsers_it = iter(parsers)

      # Parse the first occurence
      result = next(parsers_it).parse(tokens, index)
      if not result:
        return result
      index = result.index

      # Parse the next occurences
      for next_parser in parsers_it:
        next_result = next_parser.parse(tokens, index)
        if not next_result:
          return next_result
        index = next_result.index

        result = ParserResult((*result.value, next_result.value) if isinstance(result.value, tuple) else (result.value, next_result.value), index, result.errors)

      # Return the result
      return ParserResult(function(*result.value), result.index, result.errors)
    return ParserCombinator(parse_concat_more)

def combine(*parsers):
  return concat(lambda *args: tuple(args), *parsers)

def then(left, right):
  return concat(lambda _, r: r, left, right)

def before(left, right):
  return concat(lambda l, _: l, left, right)

def between(middle, left, right = None):
  right = right if right is not None else left
  return then(left, before(middle, right))


# Return the result of the left parser,
# or if that fails, backtrack and return the result of the right parser
def alternate(*parsers):
  # If no parsers are specified, then raise an error
  if len(parsers) == 0:
    raise ValueError("parsers must at least contain one item")

  # If one parser is specified, then return its result
  elif len(parsers) == 1:
    return next(iter(parsers))

  # If more parsers are specified, then alternate them
  else:
    @functools.wraps(alternate)
    def parse_alternate(tokens, index):
      parsers_it = iter(parsers)

      # Iterate over the parsers and try to parse them
      for parser in parsers_it:
        result = parser.parse(tokens, index)
        if result:
          return result

      # No parser succeeded, so return a failure
      return ParserError.unexpected(tokens, index)
    return ParserCombinator(parse_alternate)

def optional(parser, default = None):
  return alternate(parser, map_value(default, empty()))


# Return the results of multiple identical parsers as a list
def many(parser, separator = empty(), terminator = empty()):
  @functools.wraps(many)
  def parse_many(tokens, index):
    results = []

    # Parse the first occurence
    result = parser.parse(tokens, index)

    # Parse the next occurences
    while result:
      # Append the result to the list
      results.append(result.value)
      index = result.index

      # Parse the next occurence
      result = then(separator, parser).parse(tokens, index)

    # Terminate and return
    if not terminator.parse(tokens, index):
      return ParserError.unexpected(tokens, index)
    else:
      return ParserResult(results, index)
  return ParserCombinator(parse_many)

def many_sep(parser, separator):
  return many(parser, separator)

def many_sep_and_end(parser, separator):
  return many(parser, separator, separator)

def many_sep_and_optionally_end(parser, separator):
  return many(parser, separator, optional(separator))


# Return a parser that reduces an iterator of parsers using the specified function and the initializer
def reduce(function, parser, initializer = None):
  @functools.wraps(reduce)
  def parse_reduce(tokens, index):
    # Parse the first occurence, or initializer if specified
    result = initializer.parse(tokens, index) if initializer else parser.parse(tokens, index)
    if not result:
      return result
    index = result.index

    # Parse the next occurences and reduce them
    while result:
      # Parse the next occurence
      next_result = parser.parse(tokens, index)
      if not next_result:
        break
      index = next_result.index

      # Reduce the next result
      if isinstance(next_result.value, tuple):
        result = ParserResult(function(result.value, *next_result.value), next_result.index, next_result.errors)
      else:
        result = ParserResult(function(result.value, next_result.value), next_result.index, next_result.errors)

    # Return the result
    return result
  return ParserCombinator(parse_reduce)
