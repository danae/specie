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


#################################################
### Definition of the Rabobank importer class ###
#################################################

class ObjRabobankImporter(ObjImporter, typename = "RabobankImporter"):
  # Constructor
  def __init__(self, interpreter):
    super().__init__(interpreter)

  # Import a file with Rabobank transactions
  def parse(self, file_name, options):
    # Create a new transaction list
    transactions = ObjList()

    # Open the file
    with codecs.open(file_name, 'r', 'cp1252') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')

      # Iterate over the records
      for record in reader:
        # Insert the record as a transaction
        transactions.insert(self.parse_record(record, file_name))

    # Return the transactions
    return transactions

  # Parse a Rabobank record
  def parse_record(self, record, source):
    transaction = ObjTransaction()

    # Standard fields
    transaction.id = ObjString(f"rabobank:{record['Volgnr']}")
    transaction.source = ObjString(source)
    transaction.date = ObjDate(datetime.datetime.strptime(record['Datum'], '%Y-%m-%d'))
    transaction.amount = ObjMoney(ObjString(record['Munt']), ObjFloat(record['Bedrag'].replace(',', '.')))
    transaction.name = ObjString(record['Naam tegenpartij'].upper())
    transaction.address = ObjString(record['Tegenrekening IBAN/BBAN'])
    transaction.description = ObjString(re.sub('\s+', ' ', ' '.join([record['Omschrijving-1'], record['Omschrijving-2'], record['Omschrijving-3']]).strip()))

    # Extension fields
    transaction.declare_field('type', ObjString(record['Code']), public = False)

    return transaction
