# Return a truncated string if the specified string exceeds the maximum length
def ellipsis(string, length = 70):
  return (string[:length] + "...") if len(string) > length else string

# Return a list with the distinct items from the iterable appended
def distinct_append(list, iterable):
  for item in iterable:
    if item not in list:
      list.append(item)
  return list

# Return a list of the distinct items from the iterable
def distinct(iterable):
  return distinct_append([], iterable)


# Format the name of a period
def period_name(period, split_months = False):
  if split_months:
    return "{0[0]:%B %Y}".format(period)
  else:
    return "{0[0]:%Y-%m-%d} - {0[1]:%Y-%m-%d}".format(period)

# Create a table row of a period list
def row_from_periods(title, periods, split_months = False):
  return [title] + [period_name(period,split_months) for period in periods]
