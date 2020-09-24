# Specie

**Specie** is a finance manager and data query language usable from the command line, that is written in Python.

## To do

### Must
* [X] Implement token position in epressions
* [X] Fix tables printing fields at insertion order
* [X] Fix import and print statements using objects instead of their values
* [X] Replace include and import statements with native functions
* [X] Replace print statement with native function
* [X] *Grammar*: add record field get and set expressions
* [X] *Grammar*: add function definitions
* [X] Add resolver for correct closure handling
* [X] Add methods as get expression
* [ ] Add for-in expressions
* [ ] Add if-expressions
* [ ] Rework queries
* [ ] Create a new Table object for a collection of records
* [ ] Update the TransactionList class to use the new Table model

### Could
* [ ] *Performance*: Create separate parse tree that is converted into an AST after parsing
* [ ] *Neat*: Enable forward declarations in the metaclass
* [ ] *Neat*: Give type errors a meaningful type instead of the Python types
* [ ] Buffer print output (so it does not print if e.g. the function is an invalid assignment target)
