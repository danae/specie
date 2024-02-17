import functools
import re

# Define the exports for this module
__all__ = ['Rule', 'Lexer', 'LexerError', 'SyntaxError']


# Compiled newline regex pattern
newline_pattern_literal = r"\r?\n"
newline_pattern = re.compile(newline_pattern_literal)


# Class that represents a token rule
class Rule:
  # Constructor
  def __init__(self, name, pattern, replacement = 0, *, ignore = False):
    self.name = name
    self.pattern = re.compile(pattern, re.IGNORECASE)
    if callable(replacement):
      self.replacement = replacement
    elif isinstance(replacement, int):
      self.replacement = lambda m, _: m.group(replacement)
    elif isinstance(replacement, str):
      self.replacement = lambda m, _: replacement
    else:
      self.replacement = lambda m, _: None
    self.ignore = ignore


# Class that represents a location
@functools.total_ordering
class Location:
  # Constructor
  def __init__(self, line, col):
    self.line = line
    self.col = col

  # Return if this location equals another object
  def __eq__(self, other):
    if not isinstance(other, Location):
      return False
    return (self.line, self.col) == (other.line, other.col)

  # Return if this location is less than another location
  def __lt__(self, other):
    if not isinstance(other, Location):
      return NotImplemented
    return (self.line, self.col) < (other.line, other.col)

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.line!r}, {self.col!r})"

  # Convert to string
  def __str__(self):
    return f"line {self.line + 1}, col {self.col + 1}"

  # Return a location pointer string for this location in a specified string
  def point(self, string, indent = 0):
    line = newline_pattern.split(string, self.line + 1)[self.line]
    return " " * indent + line + "\n" + " " * indent + " " * self.col + "^" + " " * (len(line) - self.col - 1)


# Class that represents a token
@functools.total_ordering
class Token:
  # Constructor
  def __init__(self, name, value, location):
    self.name = name
    self.value = value
    self.location = location

  # Return if this token equals another object
  def __eq__(self, other):
    if not isinstance(other, Token):
      return False
    return (self.location, self.name, self.value) == (other.location, other.name, other.value)

  # Return if this token is less than another token
  def __lt__(self, other):
    if not isinstance(other, Token):
      return NotImplemented
    return (self.location, self.name, self.value) < (other.location, other.name, other.value)

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.name!r}, {self.value!r}, {self.location!r})"

  # Convert to string
  def __str__(self):
    if self.value is not None:
      return f"{self.name} '{self.value}' at {self.location}"
    else:
      return f"{self.name} at {self.location}"


# Class that defines the lexer
class Lexer:
  # Constructor
  def __init__(self, rules, **kwargs):
    self.rules = rules

    # Options for comment parsing
    self.comment_block = kwargs.get('comment_block')
    self.comment_inline = kwargs.get('comment_inline')
    self.comment_ignore_pattern = kwargs.get('comment_ignore_pattern')

    # Options for newline parsing
    self.newline_token = kwargs.get('newline_token', 'newline')
    self.strip_newlines = kwargs.get('strip_newlines', True)
    self.reduce_newlines = kwargs.get('reduce_newlines', True)

  # Base function for converting a string to tokens
  def tokenize_base(self, string, ignored = None):
    ignored = ignored if ignored is not None else []

    # Store the end of lines
    line_ends = []

    # Iterate over the string
    pos = 0
    while pos < len(string):
      # Check for ignored sequences
      ignored_match = next(filter(lambda m: m[0] == pos, ignored), None)
      if ignored_match:
        # Append the ignored line ends
        line_ends.extend(ignored_match[2])

        # Increase position to past the ignored sequence
        pos = ignored_match[1]
        continue

      # Determine the current location
      location = Location(len(line_ends), pos - (line_ends[-1] if line_ends else 0))

      # Check for newlines
      if newline_match := newline_pattern.match(string, pos):
        # Yield a newline token if they are tokenized
        if self.newline_token:
          yield Token(self.newline_token, None, location)

        # Append the end of the line
        line_ends.append(newline_match.end())

        # Increase position to past the newline
        pos = newline_match.end()
        continue

      # Iterate over the rules to see if they match
      token_matches = []
      for rule_index, rule in enumerate(self.rules):
        if token_match := rule.pattern.match(string, pos):
          value = rule.replacement(token_match, location)
          token = Token(rule.name, value, location)
          token_matches.append((token_match.end(), -rule_index, token, rule))

      # Check if there are matched rules
      if not token_matches:
        # We encountered an invalid character
        raise SyntaxError(f"Illegal character '{string[pos]}'", location)
      else:
        # Get the rule with the longest possible match
        token_matches.sort()
        match_tuple = token_matches[-1]

        # Ignore tuples that should be ignored
        if not match_tuple[3].ignore:
          # Yield the match token
          yield match_tuple[2]

        # Increase position to past the match
        pos = match_tuple[0]

  # Convert a string to tokens
  def tokenize(self, string):
    ignored = []

    # Ignore comments in the input string
    if self.comment_block or self.comment_inline:
      # Create the patterns for comment removal
      comment_block_pattern = (re.escape(self.comment_block[0]) + r'.*?' + re.escape(self.comment_block[1])) if self.comment_block else ''
      comment_inline_pattern = (re.escape(self.comment_inline) + r'.*?(' + newline_pattern_literal + ')') if self.comment_inline else ''
      comment_ignore_pattern = self.comment_ignore_pattern or ''

      comment_pattern = ''
      comment_pattern += comment_block_pattern or ''
      comment_pattern += '|' if comment_pattern else ''
      comment_pattern += comment_inline_pattern or ''
      comment_pattern += '|' if comment_pattern else ''
      comment_pattern += comment_ignore_pattern or ''

      # Remove the comments
      for match in re.finditer(comment_pattern, string, re.DOTALL):
        # Ignore block comments
        if self.comment_block and match.group(0).startswith(self.comment_block[0]):
          start, end = match.span(0)
          line_ends = [start + newline_match.end() for newline_match in newline_pattern.finditer(string, start, end)]
          ignored.append((start, end, line_ends))

        # Ignore inline comments
        elif self.comment_inline and match.group(0).startswith(self.comment_inline):
          start, end = match.start(0), match.start(1)
          line_ends = [start + newline_match.end() for newline_match in newline_pattern.finditer(string, start, end)]
          ignored.append((start, end, line_ends))

    # Tokenize the string
    tokens = list(self.tokenize_base(string, ignored))

    # Strip newlines
    if self.newline_token and self.strip_newlines:
      # Strip newlines from the start
      while tokens and tokens[0].name == self.newline_token:
        del tokens[0]

      # Strip newlines from the end
      while tokens and tokens[-1].name == self.newline_token:
        del tokens[-1]

    # Reduce newlines
    index = 1
    while index < len(tokens):
      if tokens[index].name == self.newline_token and tokens[index - 1].name == self.newline_token:
        del tokens[index]
      else:
        index += 1

    # Return the tokens
    return tokens


# Class that defines a lexer error
class LexerError(RuntimeError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message


# Class that defines a syntax error
class SyntaxError(LexerError):
  def __init__(self, message, location):
    self.message = message
    self.location = location

  def __str__(self):
    return f"{self.message} at {self.location}"
