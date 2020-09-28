import csv
import codecs
import datetime
import re

from .object import Obj, ObjBool, ObjInt, ObjFloat, ObjString
from .object_list import ObjList
from .object_record import FieldOptions, Field, ObjRecord
from .object_date import ObjDate
from .object_money import ObjMoney
from .object_transaction import ObjTransaction
from .object_importer import ObjImporter


#################################################
### Definition of the Rabobank importer class ###
#################################################

class ObjRabobankImporter(ObjImporter):
  # Constructor
  def __init__(self, interpreter):
    super().__init__(interpreter)

  # Import a file with Rabobank transactions
  def do(self, file_name, options):
    # Create a new transaction list
    transactions = ObjList()

    # Open the file
    with codecs.open(file_name, 'r', 'cp1252') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')

      # Iterate over the records
      for record in reader:
        # Insert the record as a transaction
        transactions.add(self.parse(record))

    # Return the transactions
    return transactions

  # Parse a Rabobank record
  def parse(self, record):
    return ObjTransaction(
      # Standard fields
      id = ObjString("rabobank:{}".format(record['Volgnr'])),
      date = ObjDate(datetime.datetime.strptime(record['Datum'], '%Y-%m-%d').date()),
      amount = ObjMoney(currency = ObjString(record['Munt']), amount = ObjFloat(record['Bedrag'].replace(',', '.'))),
      name = ObjString(record['Naam tegenpartij'].upper()),
      address = ObjString(record['Tegenrekening IBAN/BBAN']),
      description = ObjString(re.sub('\s+', ' ', ' '.join([record['Omschrijving-1'], record['Omschrijving-2'], record['Omschrijving-3']]).strip())),

      # Extension fields
      own_address = Field(ObjString(record['IBAN/BBAN']), public = False),
      own_bic = Field(ObjString(record['BIC']), public = False),
      bic = Field(ObjString(record['BIC tegenpartij']), public = False),
      type = Field(ObjString(record['Code']), public = False))
