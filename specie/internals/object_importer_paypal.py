import csv
import codecs
import datetime
import re

from colorama import Fore, Back, Style

from .object import Obj, ObjBool, ObjInt, ObjFloat, ObjString
from .object_list import ObjList
from .object_record import ObjRecord
from .object_date import ObjDate
from .object_money import ObjMoney
from .object_transaction import ObjTransaction
from .object_importer import ObjImporter


###############################################
### Definition of the PayPal importer class ###
###############################################

class ObjPayPalImporter(ObjImporter, typename = "PayPalImporter"):
  # Constructor
  def __init__(self, interpreter, primary_currency):
    super().__init__(interpreter)

    self.primary_currency = primary_currency

  # Import a file with PayPal transactions
  def parse(self, file_name, options):
    # Create a new transaction list
    transactions = ObjList()

    # Open the file
    with codecs.open(file_name, 'r', 'utf-8-sig') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')

      # Iterate over the records
      for id, record in enumerate(reader):
        # Insert the record as a transaction
        transactions.insert(self.parse_record(id, record, file_name))

    # Create a list of transactons to remove
    transactions_marked = []

    # Get all transactions with another currency than the default
    other_currencies = [t for t in transactions if t.amount.currency != self.primary_currency]
    for transaction in other_currencies:
      # Get conversion transactions with the same timestamp as this one
      conversions = [t for t in transactions if t.timestamp == transaction.timestamp and t.type == ObjString("Algemeen valutaomrekening")]

      # If there are no currency conversions, then this transaction cannot be processed
      if not conversions:
        print(f"{Style.BRIGHT}{Fore.YELLOW}Discarding unconvertible transaction '{transaction.id}'{Style.RESET_ALL}")
        transactions_marked.append(transaction)

      # Change the transaction amount to that of the correct conversion transaction
      for conversion in conversions:
        transactions_marked.append(conversion)
        if conversion.amount.currency == self.primary_currency:
          transaction.amount = conversion.amount

    # Remove all transactions that are marked
    for transaction in transactions_marked:
      transactions.delete(transaction)

    # Return the transactions
    return transactions

  # Parse a PayPal record
  def parse_record(self, id, record, source):
    transaction = ObjTransaction()

    # Helpers
    timestamp = datetime.datetime.strptime(f"{record['Datum']} {record['Tijd']} {record['Tijdzone']}", '%d-%m-%Y %H:%M:%S %Z')

    # Standard fields
    transaction.id = ObjString(f"paypal:{source}:{id:06d}:{record['Transactiereferentie']}")
    transaction.source = ObjString(source)
    transaction.date = ObjDate(timestamp)
    transaction.amount = ObjMoney(ObjString(record['Valuta']), ObjFloat(record['Net'].replace('.', '').replace(',','.')))
    transaction.name = ObjString(record['Naam'].upper())
    transaction.address = ObjString(record['Naar e-mailadres'].lower() if transaction.amount.value < ObjFloat(0.0) else record['Van e-mailadres'].lower())
    transaction.description = ObjString(record['Item Title'] or record['Note'])

    # Extension fields
    transaction.declare_field('type', ObjString(record['Type']), public = False)
    transaction.declare_field('timestamp', ObjFloat(timestamp.timestamp()), public = False)

    return transaction
