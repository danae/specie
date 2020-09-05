# TODO: Rework this to a new model

import codecs
import csv
import re

from . import ast, internals

from .utils import format_money

from collections import OrderedDict
from colorama import Fore, Back, Style
from datetime import date, datetime, timedelta
from functools import total_ordering
from os.path import isfile


# Transaction list class
class TransactionList(internals.ObjSortedList):
  # Constructor
  def __init__(self, iterable = []):
    super().__init__(iterable)

  # Return the date boundaries of this list
  def first_date(self):
    return self[0]['date'] if len(self) else internals.ObjDate(date.min)
  def last_date(self):
    return self[-1]['date'] if len(self) else internals.Objdate(date.max)

  # Get total balance
  def total(self, currency = "EUR"):
    return sum(transaction['amount'] for transaction in self if transaction['amount']['currency'] == currency) or internals.ObjMoney(currency = internals.ObjString(currency))

  # Retain transactions that match the predicate
  def where(self, function):
    return self.filter(function)

  # Retain transactions after a given date
  def where_after(self, date):
    if date is None:
      return self
    return self.where(lambda t: t['date'] >= date)

  # Retain transactions before a given date
  def where_before(self, date):
    if date is None:
      return self
    return self.where(lambda t: t['date'] <= date)

  # Retain transactions in a given period
  def where_period(self, first, last):
    return self.where_after(first).where_before(last)

  # Retain transactions with a given label
  def where_label(self, label):
    if label is None:
      return self
    return self.where(lambda t: t['label'] == label)


# Transaction reader class
class TransactionReader(TransactionList):
  # Return a transaction list that has been read
  def __new__(cls, filename, **kwargs):
    # Check the type
    if kwargs['type'] == 'rabobank':
      return RabobankTransactionReader(filename, **kwargs)
    elif kwargs['type'] == 'paypal':
      return PaypalTransactionReader(filename, **kwargs)
    else:
      raise ValueError(f"The type '{type}' is unsupported")


# Rabobank transaction reader class
class RabobankTransactionReader(TransactionReader):
  # Return a transaction list that has bean read
  def __new__(cls, filename, **kwargs):
    # Create a new transaction list
    transactions = TransactionList()

    # Open the file
    with codecs.open(filename,'r','cp1252') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')
      # Iterate over the records and parse and append them
      for record in reader:
        transactions.insert(cls.parse_transaction(record))

    # Return the transaction list
    return transactions

  # Parse a transaction from a record
  @staticmethod
  def parse_transaction(record):
    return internals.ObjTransaction(
      id = internals.ObjString("rabobank:{}".format(record['Volgnr'])),
      date = internals.ObjDate(datetime.strptime(record['Datum'], '%Y-%m-%d').date()),
      amount = internals.ObjMoney(currency = internals.ObjString(record['Munt']), amount = internals.ObjFloat(record['Bedrag'].replace(',', '.'))),
      balance = internals.ObjMoney(currency = internals.ObjString(record['Munt']), amount = internals.ObjFloat(record['Saldo na trn'].replace(',','.'))),
      own_address = internals.ObjString(record['IBAN/BBAN']),
      own_bic = internals.ObjString(record['BIC']),
      address = internals.ObjString(record['Tegenrekening IBAN/BBAN']),
      bic = internals.ObjString(record['BIC tegenpartij']),
      name = internals.ObjString(record['Naam tegenpartij'].upper()),
      type = internals.ObjString(record['Code']),
      description = internals.ObjString(re.sub('\s+', ' ', ' '.join([record['Omschrijving-1'], record['Omschrijving-2'], record['Omschrijving-3']]).strip())))


# Paypal transaction reader class
class PaypalTransactionReader(TransactionReader):
  # Return a transaction list that has bean read
  def __new__(cls, filename, currency = 'EUR', **kwargs):
    # Create a new transaction list
    transactions = TransactionList()

    # Open the file
    with codecs.open(filename, 'r', 'utf-8-sig') as file:
      # Create a dict reader
      reader = csv.DictReader(file, delimiter=',', quotechar='"')
      # Iterate over the records and parse and append them
      for index, record in enumerate(reader):
        transactions.insert(cls.parse_transaction(record, index))

    # Normalize currency conversions
    transactions_to_remove = []
    for index in range(len(transactions)):
      transaction = transactions[index]

      if index in transactions_to_remove:
        continue

      # Check if this transaction is not in the preferred currency
      if transaction.amount.currency != currency:
        # Search for the currency conversion transactions
        search_transactions = transactions[index:]
        paid_cc = next((t for t in search_transactions if t.type == "Algemeen valutaomrekening" and t.date == transaction.date and t.amount.currency == currency and t.amount.amount < 0),None)
        converted_cc = next((t for t in search_transactions if t.type == "Algemeen valutaomrekening" and t.date == transaction.date and t.amount == -transaction.amount),None)

        if paid_cc is None or converted_cc is None:
          continue

        # Change the current transaction amount
        transaction.amount = paid_cc.amount

        # Remove the currency conversions
        transactions_to_remove.append(transactions.index(paid_cc))
        transactions_to_remove.append(transactions.index(converted_cc))
        #index -= 2

      # Increase the index
      #index += 1

    # Remove the transactions
    for index in sorted(transactions_to_remove, reverse = True):
      transactions.pop(index)

    # Return the transaction list
    return transactions

  # Parse a transaction from a record
  @staticmethod
  def parse_transaction(record, index = 0):
    amount = internals.ObjMoney(currency = internals.ObjString(record['Valuta']), amount = internals.ObjFloat(record['Bruto'].replace(',','.')))

    from_email = record['Van e-mailadres'].lower()
    to_email = record['Naar e-mailadres'].lower()
    own_address = from_email if amount.amount < internals.ObjectFloat(0.0) else to_email
    address = to_email if amount.amount < internals.ObjFloat(0.0) else from_email

    return internals.ObjTransaction(
      id = internals.ObjString("paypal:{:04d}".format(index)),
      ref = internals.ObjString(record['Transactiereferentie']),
      date = internals.ObjDate(datetime.strptime(record['Datum'], '%d-%m-%Y').date()),
      amount = amount,
      own_address = internals.ObjString(own_address),
      address = internals.ObjString(address),
      name = internals.ObjString(record['Naam'].upper()),
      type = internals.ObjString(record['Type']),
      description = internals.ObjString(record['Item Title'] or record['Note']))
