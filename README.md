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
* [X] Add for-in expressions
* [X] Add if-expressions
* [X] Add optional arguments to functions
* [ ] Rework queries
* [ ] Fix PayPal imports

### Should
* [ ] Create a new Table object for a collection of records
* [ ] Update the TransactionList class to use the new Table model

### Could
* [ ] *Performance*: Create separate parse tree that is converted into an AST after parsing
* [ ] *Neat*: Enable forward declarations in the metaclass
* [ ] *Neat*: Give type errors a meaningful type instead of the Python types
* [ ] Add variadic function arguments
* [ ] Buffer print output (so it does not print if e.g. the function is an invalid assignment target)


## Queries

### Terminal
* [X] --> **select** (object) → traversable
* [X] --> **distinct** (object) → traversable
* [X] **count** → int
* [X] **fold** (callable(object, object) → object) → object
* [X] **fold** (callable(object, object) → object, object) → object
* [ ] --> **sum** (object) → number
* [ ] **min** (object) → number
* [ ] **max** (object) → number
* [ ] **average** (object) → number
* [ ] **median** (object) → number
* [X] **contains** (object) → bool
* [X] **any** (bool) → bool
* [X] **all** (bool) → bool
* [X] --> **each** → null
* [X] --> **drop** → null

### Intermediate
* [X] --> **where** (bool) → traversable
* [ ] **orderBy** (object) → traversable
* [ ] **orderByDesc** (object) → traversable
* [ ] **thenBy** (object) → traversable
* [ ] **thenByDesc** (object) → traversable
