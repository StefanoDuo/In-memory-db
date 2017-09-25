import re



class SQLParser:
   name_regex = re.compile(r"^[a-zA-Z]\w*$")

   def __init__(self, database):
      self.db = database
      self.commands = {'create': self.create_table,
                       'drop': self.drop_table,
                       'insert': self.insert_into,
                       'print': self.print_table,
                       'select': self.select}


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

      column_names = []
      column_types = []
      i = 1
      while True:
         # eats column_name token
         if not tokens or tokens[0].get_name() != 'LITERAL':
            return 'Wrong syntax for CREATE TABLE, missing column entry number {}.'.format(i)
         if not self.name_regex.match(tokens[0].get_value()):
            return 'Wrong syntax for CREATE TABLE, column_name number {} contains forbidden characters.'.format(i)
         column_name = tokens[0].get_value()
         column_names.append(column_name)
         tokens = tokens[1:]

         # eats column_type token
         if not tokens or tokens[0].get_name() != 'TYPE':
            return 'Wrong syntax for CREATE TABLE, missing column_type after column_name number {}.'.format(i)
         column_type = tokens[0].get_value()
         column_types.append(column_type)
         tokens = tokens[1:]

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
      return self.db.create_table(table_name, column_names, column_types)


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