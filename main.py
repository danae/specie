import argparse
import sys

from colorama import Fore, Back, Style
from specie import internals, interpreter, parser


# Main function
def main(args):
  print(f"specie v0.1.0 -- CLI finance manager and data query language")

  # Parse the command-line arguments
  argparser = argparse.ArgumentParser(allow_abbrev = False, add_help = False)
  argparser.add_argument('-?', '--help', action = 'help', help = "Shows this help message and quits")
  argparser.add_argument('-i', '--include', action = 'append', metavar = 'FILE', help = "Includes and evaluates the specified file")
  argparser.add_argument('-e', '--eval', action = 'append', metavar = 'EXPR', help = "Evaluates the specified expression")
  args = argparser.parse_args(args)

  # Create the interpreter
  intp = interpreter.Interpreter()

  try:
    # Interpret each specified file
    if args.include:
      for file_name in args.include:
        print(f"> include(\"{file_name}\")")
        intp.include(file_name)

    # Interpret each specified line
    if args.eval:
      for line in args.eval:
        print(f"> {line}")
        intp.execute(line)

    # Start the read-eval-print loop
    while True:
      line = input("> ")
      if not line.strip():
        continue

      while line[-1] == "\\":
        line = line[:-1] + "\n" + input(". ")
      if line == "exit":
        break

      intp.execute(line, False)

  # Catch keyboard interrupts
  except KeyboardInterrupt:
    print()

# Execute the main function if not imported
if __name__ == "__main__":
  main(sys.argv[1:])
