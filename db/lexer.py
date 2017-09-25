import re


class Token:
   def __init__(self, name, value):
      self.name = name
      self.value = value


   def get_name(self):
      return self.name


   def get_value(self):
      return self.value


   def __str__(self):
      return self.get_name() + ': ' + self.get_value()


# at the moments any whitespace inside a string literal is converted to a single space
# -- one possible solution to avoid that is to keep whitespace tokens and discard them while
# parsing if we aren't inside a string literal
class SQLLexer:
   command_regex = re.compile(r"^(?:create|load|store|drop|insert|print|select)$")
   keyword_regex = re.compile(r"^(?:table|as|into|from|where)$")
   type_regex = re.compile(r"^(?:string|int|float)$")
   separator_regex = re.compile(r"^[,\(\)]$")
   split_regex = re.compile(r"([,\(\)'])")
   arithmetic_operator_regex = re.compile(r'^[-\+\*/]$')
   boolean_operator_regex = re.compile(r'^(?:and|or|>|<|==|=>|<=)$')


   def token(self, token_value):
      token_name = ''
      if self.command_regex.match(token_value):
         token_name = 'COMMAND'
      elif self.keyword_regex.match(token_value):
         token_name = 'KEYWORD'
      elif self.separator_regex.match(token_value):
         token_name = 'SEPARATOR'
      elif self.type_regex.match(token_value):
         token_name = 'TYPE'
      elif token_value == "'":
         token_name = 'STRING_DELIMITER'
      elif self.arithmetic_operator_regex.match(token_value):
         token_name = 'ARITHMETIC_OPERATOR'
      elif self.boolean_operator_regex.match(token_value):
         token_name = 'BOOLEAN_OPERATOR'
      else:
         token_name = 'LITERAL'
      return Token(token_name, token_value)


   def tokenize(self, string):
      blocks = string.split()
      token_values = []
      for block in blocks:
         token_values.extend(self.split_regex.split(block))
      tokens = tuple(self.token(token_value) for token_value in token_values if token_value)
      return tokens