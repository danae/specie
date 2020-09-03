from colorama import Fore, Back, Style


# Money formatter
def format_money(money, display_currency = True):
  color = Fore.WHITE
  if money.amount > 0:
    color = Style.BRIGHT + Fore.GREEN
  elif money.amount < 0:
    color = Style.BRIGHT + Fore.RED

  return color + (str(money) if display_currency else str(money.amount)) + Style.RESET_ALL


# Ellipsis function
def ellipsis(string, length = 70):
  return (string[:length] + "...") if len(string) > length else string


# Format the name of a period
def period_name(period, split_months = False):
  if split_months:
    return "{0[0]:%B %Y}".format(period)
  else:
    return "{0[0]:%Y-%m-%d} - {0[1]:%Y-%m-%d}".format(period)

# Create a table row of a period list
def row_from_periods(title, periods, split_months = False):
  return [title] + [period_name(period,split_months) for period in periods]

# Print title
def print_title(title):
  title = title.upper()
  print("=" * (len(title) + 2))
  print(" " + title + " ")
  print("=" * (len(title) + 2))
