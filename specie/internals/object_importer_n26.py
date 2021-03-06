import csv
import codecs
import datetime
import re

from .object import Obj, ObjBool, ObjInt, ObjFloat, ObjString
from .object_list import ObjList
from .object_record import ObjRecord
from .object_date import ObjDate
from .object_money import ObjMoney
from .object_transaction import ObjTransaction
from .object_importer import ObjImporter


############################################
### Definition of the N26 importer class ###
############################################

class ObjN26Importer(ObjImporter, typename = "N26Importer"):
  # Constructor
  def __init__(self, interpreter):
    super().__init__(interpreter)

  # Import a file with N26 transactions
  def parse(self, file_name, options):
    # Create a new transaction list
    transactions = ObjList()

    # Open the file
    with codecs.open(file_name, 'r', 'utf-8') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')

      # Iterate over the records
      for id, record in enumerate(reader):
        # Insert the record as a transaction
        transactions.insert(self.parse_record(id, record, file_name))

    # Return the transactions
    return transactions

  # Parse an N26 record
  def parse_record(self, id, record, source):
    transaction = ObjTransaction()

    # Standard fields
    transaction.id = ObjString(f"n26:{source}:{id:06d}")
    transaction.source = ObjString(source)
    transaction.date = ObjDate(datetime.datetime.strptime(record['Date'], '%Y-%m-%d'))
    transaction.amount = ObjMoney(ObjString("EUR"), ObjFloat(record['Amount (EUR)']))
    transaction.name = ObjString(record['Payee'].upper())
    transaction.address = ObjString(record['Account number'])
    transaction.description = ObjString(record['Payment reference'])

    return transaction
