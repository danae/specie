from ..internals import *

from .object_money import ObjMoney


###########################################
### Definition of the transaction class ###
###########################################

class ObjTransaction(ObjRecord, typename = "std.Transaction"):
  # Constructor
  def __init__(self, **fields):
    super().__init__(
      id = Field(fields.get('id', ObjString()), public = False),
      date = fields.get('date', ObjDate()),
      amount = Field(fields.get('amount', ObjMoney(ObjString('EUR'), ObjFloat())), options = FieldOptions.FORMAT_ALIGN_RIGHT),
      label = fields.get('label', ObjString()),
      name = fields.get('name', ObjString()),
      address = fields.get('address', ObjString()),
      description = Field(fields.get('description', ObjString()), options = FieldOptions.FORMAT_ELLIPSIS))

    for name, field in fields.items():
      self[name] = field


  # Return if this transaction object is equal to another object
  def __eq__(self, other):
    return isinstance(other, ObjTransaction) and self['id'] == other['id']

  def method_eq(self, other: 'Obj') -> 'ObjBool':
    return ObjBool(self.__eq__(other))

  # Return the hash of this object
  def __hash__(self):
    return hash((self['id']))

  def method_asHash(self) -> 'ObjInt':
    return ObjInt(self.__hash__())

  # Compare this transaction object with another object
  def __lt__(self, other):
    if isinstance(other, ObjTransaction):
      return (self['date'], self['id']) < (other['date'], other['id'])
    return NotImplemented

  def method_lt(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__lt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __le__(self, other):
    if isinstance(other, ObjTransaction):
      return (self['date'], self['id']) <= (other['date'], other['id'])
    return NotImplemented

  def method_lte(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__le__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __gt__(self, other):
    if isinstance(other, ObjTransaction):
      return (self['date'], self['id']) > (other['date'], other['id'])
    return NotImplemented

  def method_gt(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__gt__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)

  def __ge__(self, other):
    if isinstance(other, ObjTransaction):
      return (self['date'], self['id']) >= (other['date'], other['id'])
    return NotImplemented

  def method_gte(self, other: 'ObjTransaction') -> 'ObjBool':
    if (result := self.__ge__(other)) != NotImplemented:
      return ObjBool(result)
    raise InvalidTypeException(other)
