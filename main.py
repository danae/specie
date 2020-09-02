import argparse
import sys

from specie.interpreter import Interpreter


# Main function
def main(args):
  print("specie v0.1.0 -- CLI finance manager and data query language")
  print()

  # Parse the command-line arguments
  argparser = argparse.ArgumentParser(allow_abbrev = False, add_help = False)
  argparser.add_argument('-?', '--help', action = 'help', help = "Shows this help message and quits")
  argparser.add_argument('-i', '--include', action = 'append', metavar = 'FILE', help = "Includes and evaluates the specified file")
  argparser.add_argument('-e', '--eval', action = 'append', metavar = 'EXPR', help = "Evaluates the specified expression")
  argparser.add_argument('-q', '--quit', action = 'store_true', help = "Quits the program before strting the REPL")
  args = argparser.parse_args(args)

  # Create the interpreter
  intp = Interpreter()

  try:
    # Interpret each specified file
    if args.include:
      for file_name in args.include:
        print(f"> include \"{file_name}\"")
        intp.execute_include(file_name)

    # Interpret each specified line
    if args.eval:
      for line in args.eval:
        print(f"> {line}")
        intp.execute(line)

    # Start the read-eval-print loop
    if args.quit:
      return

    while True:
      line = input("> ")
      if line == "exit":
        break

      intp.execute(line)

  except KeyboardInterrupt:
    print()

# Execute the main function if not imported
if __name__ == "__main__":
  main(sys.argv[1:])
