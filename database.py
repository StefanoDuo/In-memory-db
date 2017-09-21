from collections import OrderedDict
import itertools
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


   ### UTILITY METHODS
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


   ### INTERFACE METHODS
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


   ### UTILITY METHODS
   def parse_string(self, tokens):
      string = []
      while tokens:
         if tokens[0].get_name() == 'STRING_DELIMITER':
            string = ' '.join(string)
            string = "'" + string + "'"
            return (string, tokens[1:], True)
         string.append(tokens[0].get_value())
         tokens = tokens[1:]

      # if we get here then we finished all the tokens without finding the closing string delimiter
      return (string, [], False)


   ### INTERFACE METHODS
   def parse(self, tokens):
      #eats command token
      if not tokens:
         return 'Empty token list.'
      if tokens[0].get_name() != 'COMMAND':
         return 'Wrong syntax, missing command.'
      command = tokens[0].get_value()
      tokens = tokens[1:]

      return self.commands[command](tokens)


   ### DESCENT PARSER METHODS
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
            return 'Wrong syntax for CREATE TABLE, missing column entry number {}.'.format(i)
         if not self.name_regex.match(tokens[0].get_value()):
            return 'Wrong syntax for CREATE TABLE, column_name number {} contains forbidden characters.'.format(i)
         column_name = tokens[0].get_value()
         tokens = tokens[1:]

         # eats column_type token
         if not tokens or tokens[0].get_name() != 'TYPE':
            return 'Wrong syntax for CREATE TABLE, missing column_type after column_name number {}.'.format(i)
         column_type = tokens[0].get_value()
         tokens = tokens[1:]

         # adds column_entry to the list of parsed columns
         columns.append((column_name, column_type))

         # eats separator token
         if not tokens or tokens[0].get_name() != 'SEPARATOR':
            return 'Wrong syntax for CREATE TABLE, missing separator after column entry number {}.'.format(i)
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
      if not tokens:
         return 'Wrong syntax for PRINT, missing table_name.'
      # we can do this because we know the if order in SQLLexer.token() (a token has token_name
      # LITERAL only if it can't be matched to any other token_name)
      if tokens[0].get_name() != 'LITERAL':
         return 'Wrong syntax for PRINT, table_name is a reserved keyword.'
      if not self.name_regex.match(tokens[0].get_value()):
         return 'Wrong syntax for PRINT, table_name contains forbidden characters.'
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # checks if all the tokens have been eaten
      if tokens:
         return 'Wrong syntax for PRINT, command doesn\'t end after table_name.'

      # executes command
      return self.db.print_table(table_name)


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
         # we're always expecting a value token because we either just started or we've eaten a separator token
         if not tokens:
            return 'Wrong syntax for INSERT INTO, missing expected value entry number {}.'.format(i)

         # if the next value is a string we need to do extra operation (it's split over multiple tokens)
         if tokens[0].get_name() == 'STRING_DELIMITER':
            (value, tokens, success) = self.parse_string(tokens[1:])
            print(value)
            print_tokens(tokens)
            if not success:
               return 'Wrong syntax for INSERT INTO, something went wrong while parsing the string value number {}.'.format(i)
         # otherwise we just eat the next literal token
         elif tokens[0].get_name() == 'LITERAL':
            value = tokens[0].get_value()
            tokens = tokens[1:]
         else:
            return 'Wrong syntax for INSERT INTO, missing value entry number {}.'.format(i)
         values_list.append(value)

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


   def drop_table(self, tokens):
      # eats table_name token
      if not tokens:
         return 'Wrong syntax for DROP, missing table_name.'
      # we can do this because we know the if order in SQLLexer.token() (a token has token_name
      # LITERAL only if it can't be matched to any other token_name)
      if tokens[0].get_name() != 'LITERAL':
         return 'Wrong syntax for DROP, table_name is a reserved keyword.'
      if not self.name_regex.match(tokens[0].get_value()):
         return 'Wrong syntax for DROP, table_name contains forbidden characters.'
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # checks if all the tokens have been eaten
      if tokens:
         return 'Wrong syntax for DROP, command doesn\'t end after table_name.'

      # executes command
      return self.db.drop_table(table_name)


   def select(self, tokens):
      if not tokens:
         return 'Wrong syntax for SELECT, missing columns list.'

      # columns_list will remain empty only if * is specified instead of a columns list
      columns_list = []
      if tokens[0].get_value != '*':
         i = 0
         while True:
            # we're always expecting a column_name token because we either just started or we've eaten a separator token
            # and we discarded the * token case
            if not tokens:
               return 'Wrong syntax for SELECT, expecting column_name.'

            # eats column_name token
            if tokens[0].get_name() != 'LITERAL':
               return 'Wrong syntax for SELECT, missing column name number {}.'.format(i)

            columns_list.append(tokens[0].get_value())
            tokens = tokens[1:]

            # stops parsing if we don't find a separator token
            if not tokens:
               return 'Wrong syntax for SELECT, missing FROM clause'
            if tokens[0].get_name() != 'SEPARATOR':
               break

            tokens = tokens[1:]
            i += 1

      # eats from token
      if tokens[0].get_value() != 'from':
         return 'Wrong syntax for SELECT, missing FROM clause'
      tokens = tokens[1:]

      i = 0
      tables_list = []
      while True:
         # we're always expecting a table_name token because we either just started or we've eaten a separator token
         # and we discarded the * token case
         if not tokens:
            return 'Wrong syntax for SELECT, missing table name number {}.'.format(i)

         # eats table_name token
         if tokens[0].get_name() != 'LITERAL':
            return 'Wrong syntax for SELECT, missing column name number {}.'.format(i)

         tables_list.append(tokens[0].get_value())
         tokens = tokens[1:]

         # the where clause is optional
         if not tokens:
            return self.db.select(columns_list, tables_list)

         if tokens[0].get_name() != 'SEPARATOR':
            break

         tokens = tokens[1:]
         i += 1

      # eats where token
      if tokens[0].get_value() != 'where':
         return 'Wrong syntax for SELECT, expecting where clause after tables list.'

      return self.db.select(columns_list, tables_list)


   def transact(self, query):
      pass


   def load(self, query):
      pass


   def store(self, query):
      pass



# TODO: define a class for each type to simplify literals parsing etc
class TypeString:
   def __init__(self, string):
      self.is_NaN = False
      self.is_NOVALUE = False


   def __str__(self):
      return "'" + self.value + "'"



class Row:
   def __init__(self, row):
      self.row = tuple(row)


   # TODO: will be replaced by TypeClass.__str__
   def stringify_value(self, value):
      if type(value) is str:
         return "'" + value + "'"
      return str(value)


   def __getitem__(self, key):
      return self.row[key]


   def __str__(self):
      stringified_values = (self.stringify_value(value) for value in self.row)
      return ','.join(stringified_values)


   def __iter__(self):
      return iter(self.row)



class Table:
   def __init__(self, columns_list):
      self.column_names = tuple(column[0] for column in columns_list)
      self.column_types = tuple(column[1] for column in columns_list)
      self.name_to_index = {column_name: index for index, column_name in enumerate(self.column_names)}
      self.rows = []


   ### UTILITY METHODS
   def __str__(self):
      table_header = self.get_header_string()
      stringified_rows = (str(row) for row in self.get_rows())
      table_content = '\n'.join(stringified_rows)
      return table_header + '\n' + table_content


   ### INTERFACE METHODS
   def insert_row(self, row):
      self.rows.append(Row(row))
      return ''


   def get_header_string(self):
      columns = (' '.join(column) for column in zip(self.column_names, self.column_types))
      return ','.join(columns)


   def get_column_types(self):
      return self.column_types


   def get_column_type_by_name(self, column_name):
      index = self.get_index_from_name(name)
      return self.get_column_type_by_name_index(index)


   def get_column_type_by_index(self, column_index):
      return self.column_types[column_index]


   def get_column_names(self):
      return self.column_names


   def get_rows(self):
      return self.rows


   def get_index_by_name(self, name):
      return self.name_to_index[name]



class Database:
   # TODO: value_regex will be moved inside each TypeClass
   value_regex = {'float': re.compile(r"^-?\d*.\d*$"),
                  'int': re.compile(r"^-?\d*$"),
                  'string': re.compile(r"^.*$")}
   value_parse = {'string': lambda x: x[1:-1],
                  'float': float,
                  'int': int,}

   def __init__(self):
      self.tables = {}


   def create_table(self, table_name, columns_list):
      if table_name in self.tables:
         return 'A table named {} alredy exists in memory.'.format(table_name)

      self.tables[table_name] = Table(columns_list)
      return ''


   def print_table(self, table_name):
      if table_name not in self.tables:
         return 'A table named {} doesn\'t exists in memory.'.format(table_name)

      table = self.tables[table_name]
      return str(table)


   def drop_table(self, table_name):
      if table_name not in self.tables:
         return 'A table named {} doesn\'t exists in memory.'.format(table_name)

      del self.tables[table_name]
      return ''


   def insert_into(self, table_name, values_list):
      if table_name not in self.tables:
         return 'A table named {} doesn\'t exists in memory.'.format(table_name)

      table = self.tables[table_name]
      types = table.get_column_types()
      parsed_values = []
      i = 0
      for value, column_type in itertools.zip_longest(values_list, types):
         if not column_type:
            return 'There are too many values in the values list.'
         if not value:
            return 'There are too few values in the values list.'
         if not self.value_regex[column_type].match(value):
            return 'Value entry number {} isn\'t of type {}'.format(i, column_type)
         parsed_values.append(self.value_parse[column_type](value))

      return table.insert_row(parsed_values)

   # TODO: instead of creating a list every time start using generators/iterators if possible
   # at the moment a column name is bound to the first table with contains a column with the same name
   def select(self, columns_list, tables_list):
      # check if all the tables exist and create the tables scope
      tables_scope = {}
      for table_name in tables_list:
         if table_name not in self.tables:
            return 'A table named {} doesn\'t exists in memory.'.format(table_name)
         tables_scope[table_name] = self.tables[table_name]

      # check if all the columns_name exist in the tables scope, and store info about every column
      columns = []
      for column_name in columns_list:
         for table_name, table in tables_scope.items():
            if column_name in table.get_column_names():
               column_index = table.get_index_by_name(column_name)
               column_type = table.get_column_types()[column_index]
               column_entry = {'column_name': column_name,
                               'column_type': column_type,
                               'table_name': table_name,
                               'column_index': column_index}
               columns.append(column_entry)
               break
         else: # executes only if the for loop terminates by exhaustion (not with a break)
            return 'A column named {} doesn\'t exists inside the specified tables list.'.format(columns_name)

      # we create the temporary table described by the select
      columns_list = tuple((column['column_name'], column['column_type']) for column in columns)
      select_table = Table(columns_list)

      # groups columns by table_name and saves the column order for the select table
      columns_by_table = {}
      select_columns_order = []
      for select_index, column in enumerate(columns):
         select_columns_order.append(select_index)
         table_name = column['table_name']
         column_index = column['column_index']
         if table_name in columns_by_table:
            columns_by_table[table_name].append(column_index)
         else:
            columns_by_table[table_name] = [column_index]

      # retrieves values needed keeping them grouped by table
      values_by_table = []
      for table_name, columns in columns_by_table.items():
         selected_rows = []
         rows = tables_scope[table_name].get_rows()
         for row in rows:
            selected_row = []
            for column_index in columns:
               selected_row.append(row[column_index])
            selected_rows.append(selected_row)
         values_by_table.append(tuple(selected_rows))

      cartesian_product = tuple(itertools.product(*values_by_table))

      merged_rows = []
      for row in cartesian_product:
         merged_row = []
         for table in row:
            merged_row.extend(table)
         merged_rows.append(merged_row)

      ordered_rows = []
      for row in merged_rows:
         ordered_row = [row for _, row in sorted(zip(select_columns_order, row))]
         ordered_rows.append(ordered_row)

      for row in ordered_rows:
         select_table.insert_row(row)

      return str(select_table)



def print_tokens(tokens):
   for token in tokens:
      print(token)



# TODO: implement a real test case
if __name__ == '__main__':
   lexer = SQLLexer()
   database = Database()
   parser = SQLParser(database)


   if False:
      print('STARTING QUERY SYNTAX TEST')
      queries = ('create table Test ()',
                 'create tabsle Test (col1 int, col2 float, col3 string)',
                 'creates table Test (col1 int, col2 float, col3 string)',
                 'create tables Test (col1 int, col2 float, col3 string)',
                 'credate table Test (col1 int, col2 float, col3 string)',
                 'create table T(est int (col1 int, col2 float, col3 string)',
                 'create table Test (col1 ints, col2 float, col3 string)',
                 'create table Test (col1 int, col2 fldoat, col3 string)',
                 'create table Test (col1 int, col2 float, col3 strindg)',
                 'create table Test (col1 Int, col2 float, col3 string)',
                 'create table Test (col1 int, col2 Float, col3 string)',
                 'create table Test (col1 int, col2 float, col3 String)',
                 'create table Test (col1 int, col2 float, col3 string,)',
                 'create table Test (col1 int, col2 float, col3 string',
                 'create table Test (col1 int, col2 float, col3 string) :::',
                 'create table Test (c`ol1 int, col2 float col3 string)')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING CREATE TABLE TEST')
      queries = ['create table Test (c1 int, c2 int, c3 float)',
                 'create table Test2 (c11 int, c12 string, c13 float)',
                 'create table Test (c string)',
                 'create table Test2 (jjjj float)']
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         # print_tokens(tokens)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print create',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING INSERT TABLE TEST')
      queries = ('insert into Testd values 4,2,3.2',
                 'insert into Test values 0,1,2',
                 'insert into Test values 3,4,5',
                 'insert into Test values 6,7,8',
                 'insert into Test values 0,2,',
                 'insert into Test values 4,,3.2',
                 'insert into Test values 4,3,3.2, 4,22',
                 'insert into Test values 4,4',
                 'insert into Test2 values 0,\'Hello World!\',3.2',
                 'insert into Test2 values 1,\'Hello World!\',3.2',
                 'insert into Test2 values 2,\'Hello World!\',3.2',
                 'insert into Test2 values 3,\'Hello World!\',3.2',
                 'insert into Test2 values 4,\'Hello World!\',3.2')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print into as',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING DROP TABLE TEST')
      queries = ('drop Test',
                 'drop Test2',
                 'drop into as',
                 'drop   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print into as',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING SELECT TABLE TEST')
      queries = ('select c3, c2, c1 from Test',
                 'select c1, c2, c3, c11 from Test, Test2')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')