from collections import OrderedDict
from itertools import zip_longest
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


# TODO: add single quotes to the keywords or string separator
class SQLLexer:
   command_regex = re.compile(r"^(?:create|load|store|drop|insert|print|select)$")
   keyword_regex = re.compile(r"^(?:table|as|into|from|where)$")
   type_regex = re.compile(r"^(?:string|int|float)$")
   separator_regex = re.compile(r"^[,\(\)]$")
   split_regex = re.compile(r"([,\(\)])")
   # operator support will be added later
   # arithmetic_operator_regex = re.compile(r'[-\+\*/]')
   # boolean_operator_regex = re.compile(r'and|or')


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



class SQLParser:
   name_regex = re.compile(r"^[a-zA-Z]\w*$")


   def __init__(self, database):
      self.db = database
      self.commands = {'create': self.create_table,
                       'load': self.load,
                       'store': self.store,
                       'drop': self.drop_table,
                       'insert': self.insert_into,
                       'print': self.print_table,
                       'select': self.select}


   def parse(self, tokens):
      #eats command token
      if not tokens:
         return 'Empty token list.'
      if tokens[0].get_name() != 'COMMAND':
         return 'Wrong syntax, missing command.'
      command = tokens[0].get_value()
      tokens = tokens[1:]

      return self.commands[command](tokens)


   def create_table(self, tokens):
      # eats table token
      if not tokens or tokens[0].get_value() != 'table':
         return 'Wrong syntax for CREATE TABLE, missing TABLE after CREATE.'
      tokens = tokens[1:]

      # eats table_table token
      if not tokens or tokens[0].get_name() != 'LITERAL':
         return 'Wrong syntax for CREATE TABLE, missing table_name.'
      if not self.name_regex.match(tokens[0].get_value()):
         return 'Wrong syntax for CREATE TABLE, table_name contains forbidden characters.'
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # eats '(' token
      if not tokens or tokens[0].get_value() != '(':
         return 'Wrong syntax for CREATE TABLE, missing column list'
      tokens = tokens[1:]

      columns = []
      i = 1
      while True:
         # eats column_name token
         if not tokens or tokens[0].get_name() != 'LITERAL':
            return 'Wrong syntax for CREATE TABLE, missing column in column entry number {}.'.format(i)
         if not self.name_regex.match(tokens[0].get_value()):
            return 'Wrong syntax for CREATE TABLE, column_name contains forbidden characters in column entry number {}.'.format(i)
         column_name = tokens[0].get_value()
         tokens = tokens[1:]

         # eats column_type token
         if not tokens or tokens[0].get_name() != 'TYPE':
            return 'Wrong syntax for CREATE TABLE, missing column_type after column_name in column entry number {}.'.format(i)
         column_type = tokens[0].get_value()
         tokens = tokens[1:]

         # adds column_entry to the list of parsed columns
         columns.append((column_name, column_type))

         # eats separator token
         if not tokens or tokens[0].get_name() != 'SEPARATOR':
            return 'Wrong syntax for CREATE TABLE, missing separator after column_element in column entry number {}.'.format(i)
         if tokens[0].get_value() == ')':
            tokens = tokens[1:]
            break
         if tokens[0].get_value() != ',':
            return 'Wrong syntax for CREATE TABLE, wrong ( character inside columns list.'
         tokens = tokens[1:]
         i += 1

      # checks if all the tokens have been eaten
      if tokens:
         return 'Wrong syntax for CREATE TABLE, command doesn\'t end after )'

      # executes command
      return self.db.create_table(table_name, columns)


   def print_table(self, tokens):
      # eats table_name token
      if not tokens or not self.name_regex.match(tokens[0].get_value()):
         return 'Wrong syntax for PRINT, missing table_name.'
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # checks if all the tokens have been eaten
      if tokens:
         return 'Wrong syntax for PRINT, command doesn\'t end after table_name.'

      # executes command
      return self.db.print_table(table_name)

   # TODO: add support for single spaces inside string values
   def insert_into(self, tokens):
      # eats into token
      if not tokens or tokens[0].get_value() != 'into':
         return 'Wrong syntax for INSERT INTO, missing into after insert.'
      tokens = tokens[1:]

      # eats table_table token
      if not tokens or tokens[0].get_name() != 'LITERAL':
         return 'Wrong syntax for INSERT INTO, missing table_name.'
      if not self.name_regex.match(tokens[0].get_value()):
         return 'Wrong syntax for INSERT INTO, table_name contains forbidden characters.'
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # eats values token
      if not tokens or tokens[0].get_value() != 'values':
         return 'Wrong syntax for INSERT INTO, missing values after table_name.'
      tokens = tokens[1:]

      values_list = []
      i = 1
      while True:
         # eats value token
         if not tokens or tokens[0].get_name() != 'LITERAL':
            return 'Wrong syntax for INSERT INTO, missing value entry number {}.'.format(i)
         values_list.append(tokens[0].get_value())
         tokens = tokens[1:]

         # stops parsing if tokens are over
         if not tokens:
            return self.db.insert_into(table_name, values_list)

         # eats separator tokens if tokens aren't over
         if tokens[0].get_name() != 'SEPARATOR':
            return 'Wrong syntax for INSERT INTO, missing separator after value in entry number {}.'.format(i)
         if tokens[0].get_value() != ',':
            return 'Wrong syntax for INSERT INTO, expecting , got something else.'
         tokens = tokens[1:]
         i += 1

      # this code can't be executed
      return 'Something went wrong while parsing an INSERT INTO command.'


   def transact(self, query):
      pass


   def load(self, query):
      pass


   def store(self, query):
      pass


   def drop_table(self, query):
      pass


   def select(self, query):
      pass



class Column:
   def __init__(self, column_type):
      self.type = column_type
      self.values = []
      


class Table:
   def __init__(self, columns_list):
      self.header = tuple((column[0], column[1]) for column in columns_list)
      self.name_to_index = {column[0]: index for index, column in enumerate(columns_list)}
      self.rows = []


   def get_header(self):
      columns = (' '.join(tuple) for tuple in self.header)
      return ','.join(columns)


   def insert_row(self, row):
      self.rows.append(row)
      return ''


   def get_num_of_columns(self):
      return length(self.name_to_index)


   def get_types(self):
      return (tuple[1] for tuple in self.header)


   def get_rows(self):
      return self.rows



class Database:
   value_regex = {'float': re.compile(r"^-?\d*.\d*$"),
                  'int': re.compile(r"^-?\d*$"),
                  'string': re.compile(r"^'.*'$")}
   value_parse = {'string': lambda x: x[1:-1],
                  'float': float,
                  'int': int,}

   def __init__(self):
      self.tables = {}


   def stringify_row(self, row):
      stringified_row = []
      for value in row:
         if type(value) is str:
            stringified_row.append("'" + value + "'")
         else:
            stringified_row.append(str(value))
      return stringified_row


   def create_table(self, table_name, columns_list):
      if table_name in self.tables:
         return 'A table named {} alredy exists in memory.'.format(table_name)

      self.tables[table_name] = Table(columns_list)
      return ''


   def print_table(self, table_name):
      if table_name not in self.tables:
         return 'A table named {} doesn\'t exists in memory.'.format(table_name)

      table = self.tables[table_name]
      header = table.get_header()
      # first we stringify each value following the standard
      stringified_rows = (self.stringify_row(row) for row in table.get_rows())
      # then we join each stringified row
      joined_rows = (','.join(row) for row in stringified_rows)
      return header + '\n' + '\n'.join(joined_rows)


   def insert_into(self, table_name, values_list):
      if table_name not in self.tables:
         return 'A table named {} doesn\'t exists in memory.'.format(table_name)

      table = self.tables[table_name]
      types = table.get_types()
      parsed_values = []
      i = 0
      for value, column_type in zip_longest(values_list, types):
         if not column_type:
            return 'There are too many values in the values list.'
         if not value:
            return 'There are too few values in the values list.'
         if not self.value_regex[column_type].match(value):
            return 'Value entry number {} isn\'t of type {}'.format(i, column_type)
         parsed_values.append(self.value_parse[column_type](value))

      return table.insert_row(parsed_values)



def print_tokens(tokens):
   for token in tokens:
      print(token)



if __name__ == '__main__':
   lexer = SQLLexer()
   database = Database()
   parser = SQLParser(database)


   if False:
      print('STARTING QUERY SYNTAX TEST')
      queries = ('create table Prova ()',
                 'create tabsle Prova (col1 int, col2 float, col3 string)',
                 'creates table Prova (col1 int, col2 float, col3 string)',
                 'create tables Prova (col1 int, col2 float, col3 string)',
                 'credate table Prova (col1 int, col2 float, col3 string)',
                 'create table P(rova int (col1 int, col2 float, col3 string)',
                 'create table Prova (col1 ints, col2 float, col3 string)',
                 'create table Prova (col1 int, col2 fldoat, col3 string)',
                 'create table Prova (col1 int, col2 float, col3 strindg)',
                 'create table Prova (col1 Int, col2 float, col3 string)',
                 'create table Prova (col1 int, col2 Float, col3 string)',
                 'create table Prova (col1 int, col2 float, col3 String)',
                 'create table Prova (col1 int, col2 float, col3 string,)',
                 'create table Prova (col1 int, col2 float, col3 string',
                 'create table Prova (col1 int, col2 float, col3 string) :::',
                 'create table Prova (c`ol1 int, col2 float col3 string)')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING CREATE TABLE TEST')
      queries = ['create table Prova (c1 int, c2 int, c3 float)',
                 'create table Prova2 (c1 int, c2 string, c3 float)',
                 'create table Prova (c string)',
                 'create table Prova2 (jjjj float)']
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         # print_tokens(tokens)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Prova',
                 'print Prova2',
                 'print Prork',
                 'print   Prova')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING INSERT TABLE TEST')
      queries = ('insert into Prova values 4,2,3.2',
                 'insert into Prova values 4,2,.2',
                 'insert into Prova values 4,2,3.',
                 'insert into Prova values 0,2,',
                 'insert into Prova values 4,,3.2',
                 'insert into Prova values 4,3,3.2, 4,22',
                 'insert into Prova values 4,4',
                 'insert into Prova2 values 4,\'cicciocarlino\',3.2')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         print_tokens(tokens)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Prova',
                 'print Prova2',
                 'print Prork',
                 'print   Prova')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')