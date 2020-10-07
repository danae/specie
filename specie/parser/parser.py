# Class that defines a parser
class Parser:
  # Constructor
  def __init__(self, function, sync_tokens = []):
    self.function = function
    self.sync_tokens = sync_tokens

  # Parse the iterable of tokens starting at the specified index
  def parse(self, tokens, index, errors = []):
    result = self.function(tokens, index)
    if isinstance(result, ParserResult):
      # Return the result
      return ParserResult(result.value, result.index, result.errors + errors)
    else:
      if not self.sync_tokens:
        # If no error or sync tokens, then just return the error
        return ParserResult(None, index, errors + [result])
      else:
        # Walk over the tokens until a synchronization point
        for i in range(index, len(tokens)):
          token = tokens[i]
          if token.name in self.sync_tokens and i + 1 < len(tokens):
            #print(f"Caught '{result}', now synchronizing at {tokens[i + 1]}")
            #print(f"    {errors + [result]}")
            return self.parse(tokens, i + 1, errors + [result])

        # End is reached, so return the previously caught error
        return ParserResult(None, index, errors + [result])

  # Parse the iterable of tokens, but fail if not all tokens are consumed
  def parse_strict(self, tokens, index):
    result = self.parse(tokens, index)
    if result.index != len(tokens):
      if not result:
        raise result.errors[0]
      else:
        raise ParserError(f"Unexpected token {tokens[result.index]}, the parser didn't consume all tokens")
    return result

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.function!r})"


# Class that defines a parser result
class ParserResult:
  # Constructor
  def __init__(self, value, index, errors = []):
    self.value = value
    self.index = index
    self.errors = errors

  # Return the truthyness of the result
  def __bool__(self):
    return not self.errors

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.value!r}, {self.index!r}, {self.errors!r})"


# Class that defines a parser error
class ParserError(Exception):
  # Constructor
  def __init__(self, message, location = None):
    self.message = message + (f" at {location}" if location else "")
    self.location = location

  # Convert to representation
  def __repr__(self):
    return f"{self.__class__.__name__}({self.message!r}, {self.location!r})"

  # Return an unexpected token error
  @classmethod
  def unexpected(cls, tokens, index, expected = None):
    if index < len(tokens):
      return cls(f"Unexpected token {tokens[index]}" + (f", expected {expected}" if expected else ""))
    else:
      return cls(f"Unexpected end of tokens" + (f", expected {expected}" if expected else ""))
