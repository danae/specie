from . import internals, utils


# Class that defines a query on a list
class Query:
  # Constructor
  def __init__(self, table, action, predicate):
    self.table = table
    self.action = action
    self.predicate = predicate


  ### Definition of helper functions ###

  # Return a mapped record using the specified expressions
  def _map(self, interpreter, expressions):
    def _map_lambda(item):
      record = internals.ObjRecord()

      interpreter.begin_scope(item)
      for expression in expressions:
        record[str(expression)] = interpreter.evaluate(expression)
      interpreter.end_scope()

      return record
    return _map_lambda


  ### Definition of query action functions ###

  # Return a table that adheres to the predicate
  def test(self):
    if self.predicate is not None:
      return self.table.filter(lambda item: self.predicate(item))
    else:
      return self.table

  # Execute the query
  def execute(self, interpreter):
    action = self.action.name.value

    # Query actions
    if action == 'get':
      return self.execute_get(interpreter, self.action.args)
    elif action == 'apply':
      return self.execute_apply(interpreter, self.action.args)
    elif action == 'delete':
      return self.execute_delete(interpreter, self.action.args)
    elif action == 'group':
      return self.execute_group(interpreter, self.action.args)

    # No matching action found
    raise internals.RuntimeException(f"Undefined query action '{action}'", self.action.name.location)

  # Execute a get query
  def execute_get(self, interpreter, args):
    # Apply the predicate
    table_test = self.test()

    # If there are arguments specified, then map the table
    if args:
      # Return the table with the records mapped to the arguments
      return table_test.map(self._map(interpreter, args))
    else:
      # Return the original table
      return table_test

  # Execute an apply query
  def execute_apply(self, interpreter, args):
    # Apply the predicate
    table_test = self.test()

    # Evaluate the arguments
    args = interpreter.evaluate(args)
    if not isinstance(args[0], internals.ObjCallable):
      raise internals.RuntimeException("The argument of an apply query must be callable")

    # Iterate over the tested table
    for item in table_test:
      # Apply the callable with the item
      args[0](item)

    # Return the number of matched items
    return internals.ObjInt(len(table_test))

  # Execute a delete query
  def execute_delete(self, interpreter, args):
    # Apply the predicate
    table_test = self.test()

    # Iterate over the tested table
    for item in table_test:
      # Delete the item from the original table
      self.table.delete(item)

    # Return the number of matched items
    return internals.ObjInt(len(table_test))

  # Execute a group query
  def execute_group(self, interpreter, args):
    # Apply the predicate
    table_test = self.test()

    # Return a list of distinct matches
    return internals.ObjList(utils.distinct(interpreter.evaluate_scope(args[0], item) for item in table_test))
