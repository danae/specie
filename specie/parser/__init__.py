from .lexer import Token, Lexer, LexerError, SyntaxError
from .parser import ParserError, UnexpectedEndOfTokens, UnexpectedToken
from .grammar import rules, grammar

# Define the exports for this module
__all__ = ['parse', 'LexerError', 'SyntaxError', 'ParserError', 'UnexpectedEndOfTokens', 'UnexpectedToken']


# Parse an input string to an abstract syntax tree
def parse(string):
  # Create the lexer
  lexer = Lexer(rules, comment_inline = '#', comment_block = ('#-', '-#'), comment_ignore_pattern = r'"((?:[^"\\]|\\.)*)"')

  # Parse the inout string to a list of tokens
  tokens = lexer.tokenize(string)

  # Parse the list of tokens to an abstract syntax tree
  result = grammar.parse(tokens, 0)
  return result.value
