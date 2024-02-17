import functools

from rich import box
from rich.console import Console
from rich.table import Table

from . import internals, utils


# Create the console
console = Console()


#############################################
### Definition of the table utility class ###
#############################################

"""
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

  # Covnert to bool
  def __bool__(self):
    return bool(self.rows)

  # Convert to string
  def __str__(self):
    # Calculate the width of the columns
    widths = []
    for column_index in range(0, self.column_count()):
      column = self.get_column(column_index)
      # TODO: Neat ellipsis
      width = min(max(len(cell) for cell in column), 80)
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
        # TODO: Neat ellipsis
        strings.append(fmt.format(*(s[:80] for s in row)))
    strings.append("")

    # Return the strings
    return "\n".join(strings)
"""


### Definition of functions to print objects ###

# Print a title
def title(string: 'ObjString') -> 'ObjNull':
  console.print()
  console.rule(f"[bold]{string}", align = 'left')
  return internals.ObjNull()

# Print an object
def print_object(*objects: 'Obj') -> 'ObjNull':
  # If there is a single object, then print it with details
  if len(objects) == 1:
    object = objects[0]
    if isinstance(object, internals.ObjRecord) and object.__class__.prettyprint:
      print_record(object)
    elif isinstance(object, internals.ObjMap):
      print_map(object)
    elif isinstance(object, internals.ObjList):
      print_list(object)
    else:
      console.print(str(object))

  # If there are multiple objects, concatenate them
  elif len(objects) > 1:
    console.print("".join(str(object) for object in objects))

  return internals.ObjNull()

# Print a record oject
def print_record(record: 'ObjRecord'):
  table = Table(box = box.SQUARE)

  table.add_column('field', justify = 'left', style = 'cyan', no_wrap = True)
  table.add_column('value', justify = 'left', no_wrap = True)

  for field, value in record:
    table.add_row(str(field), str(value))

  console.print(table)

# Print a map oject
def print_map(map: 'ObjMap'):
  table = Table(box = box.SQUARE)

  table.add_column('key', justify = 'left', style = 'cyan', no_wrap = True)
  table.add_column('value', justify = 'left', no_wrap = True)

  for key, value in map.elements.items():
    table.add_row(str(key), str(value))

  console.print(table)

# Print a list object
def print_list(list: 'ObjList'):
  # Check if the list is empty
  if not list:
    print("No items in the list")
  else:
    # Check if this list is a list of records
    if all(isinstance(item, internals.ObjRecord) for item in list):
      print_table(list)

    # Otherwise just print every item on its own line
    else:
      for item in list:
        console.print(f"- {item}")

# Print a table object
def print_table(list: 'ObjList'):
  # Get all fields
  fields = functools.reduce(utils.distinct_append, ([name for name, field in record.fields.items() if field.public] for record in list), [])

  # Print the list in table form
  table = Table(box = box.SQUARE)

  for field in fields:
    table.add_column(field, justify = 'left')

  for record in list:
    table.add_row(*[str(record.get_field_or(name, "")) for name in fields])

  console.print(table)
