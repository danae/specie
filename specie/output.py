import functools

from . import internals


### Definition of the table utility class ###

class Table:
  # Constructor
  def __init__(self):
    self.rows = []
    self.right_align = {}

  # Return a row by index
  def get_row(self, row_index):
    return self.rows[row_index]

  # Append a row
  def append_row(self, row_cells):
    # Check if the number of cells fits
    if self.rows and len(row_cells) != self.column_count():
      raise ValueError("Only rows with {} cells can be appended to this table".format(self.column_count()))

    # Append the cells
    self.rows.append([str(cell) for cell in row_cells])

  # Append a separator row
  def append_separator_row(self):
    self.append_row(["---"] * self.column_count())

  # Append an empty row
  def append_empty_row(self):
    self.append_row([""] * self.column_count())

  # Append a title row
  def append_title_row(self, title):
    self.append_row([title] + [""] * self.column_count())

  # Return a column by index
  def get_column(self, column_index):
    return [row[column_index] for row in self.rows]

  # Append a column
  def append_column(self, column_cells):
    # If no rows present, then add the cells as rows
    if not self.rows:
      self.rows = [[str(cell)] for cell in column_cells]

    # Otherwise append each cell to the row
    else:
      # Check if the number of cells fits
      if len(column_cells) != self.row_count():
        raise ValueError("Only columns with {} cells can be appended to this table".format(self.row_count()))

      # Append the cells
      for index, row in enumerate(self.rows):
        row.append(str(column_cells[index]))

  # Return the number of rows
  def row_count(self):
    return len(self.rows)

  # Return the number of columns
  def column_count(self):
    return len(self.rows[0]) if self.rows else 0

  # Convert to string
  def __str__(self):
    # Calculate the width of the columns
    widths = []
    for column_index in range(0,self.column_count()):
      column = self.get_column(column_index)
      width = max(len(cell) for cell in column)
      widths.append(width)

    # Create the format string
    fmt = []
    for index, width in enumerate(widths):
      fmt.append("{:" + (">" if self.right_align.get(index, False) else "<") + str(width) + "}")
    fmt = " | ".join(fmt)

    separators = " | ".join(("-" * width) for width in widths)

    # Format the rows and return them
    strings = [""]
    for row in self.rows:
      # Check if this is a separator row
      if row == ["---"] * self.column_count():
        strings.append(separators)
      # Otherwise append the row
      else:
        strings.append(fmt.format(*row))
    strings.append("")

    # Return the strings
    return "\n".join(strings)


### Definition of functions to print objects ###

# Print an object
def print_object(object, **kwargs):
  if isinstance(object, internals.ObjRecord):
    print_record(object, **kwargs)
  elif isinstance(object, internals.ObjList):
    print_list(object, **kwargs)
  else:
    print(object)

# Print a record oject
def print_record(record, **kwargs):
  table = Table()
  table.append_row(['field', 'value'])
  table.append_separator_row()

  for name in record.iter_fields():
    value = record.get_field(name)
    table.append_row([name, value])

  print(table)

# Print a list object
def print_list(list, **kwargs):
  print(f"{len(list)} items:")

  # Check if this list is a list of records
  if all(isinstance(item, internals.ObjRecord) for item in list):
    # Get all fields
    if (fields := kwargs.get('fields', None)) is not None:
      all_fields = set(str(field) for field in fields)
    else:
      # TODO: implement sorted in insertion order
      all_fields = functools.reduce(lambda a, b: a | set(b), (record.names() for record in list), set())

    # Print the list in table form
    table = Table()
    table.append_row(all_fields)
    table.append_separator_row()

    for record in list:
      table.append_row([record.get(name, "") for name in all_fields])

    print(table)

  # Otherwise just print every item on its own line
  else:
    for item in list:
      print(f"- {item}")
