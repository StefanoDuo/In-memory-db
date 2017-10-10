import re


# NOTES
# 1) instead of first creating an AST then applying it's semantinc meaning (which could be
#    done by two different modules) i preferred to do both in one step inside the parse because
#    it was quite trivial to build the data structures needed by the database interface while
#    parsing the command (for the sql subset i decided to implement), this way i still got to
#    learn about lexical analysis, parsing etc. without complicating things too much
# 2) the "database virtual machine" offers a function oriented API because that was the easiest
#    way to implent one, even though this way operations optimization is way more difficult (if
#    not entirely impossible)

# TODO: definite exceptions classes for every error type
class SQLParser:
   name_regex = re.compile(r"^[a-zA-Z]\w*$")


   operators_priority = {'+': 2,
                         '-': 2,
                         '*': 2,
                         '/': 2,
                         '>': 1,
                         '>=': 1,
                         '<': 1,
                         '<=': 1,
                         '=': 1,
                         '!=': 1,
                         'and': 0,
                         'or': 0}


   def __init__(self):
      self.commands = {'create': self.create_table,
                       'drop': self.drop_table,
                       'insert': self.insert_into,
                       'print': self.print_table,
                       'select': self.select}


   def parse(self, tokens):
      #eats command token
      if not tokens:
         raise ValueError('Empty token list.')
      if tokens[0].get_name() != 'COMMAND':
         raise ValueError('Wrong syntax, missing command.')
      command = tokens[0].get_value()
      tokens = tokens[1:]

      return self.commands[command](tokens)


   def create_table(self, tokens):
      # eats table token
      if not tokens or tokens[0].get_value() != 'table':
         raise ValueError('Wrong syntax for CREATE TABLE, missing TABLE after CREATE.')
      tokens = tokens[1:]

      # eats table_table token
      if not tokens or tokens[0].get_name() != 'LITERAL':
         raise ValueError('Wrong syntax for CREATE TABLE, table_name is a reserved keyword.')
      if not self.name_regex.match(tokens[0].get_value()):
         raise ValueError('Wrong syntax for CREATE TABLE, table_name contains forbidden characters.')
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      if not tokens:
         raise ValueError('Wrong syntax for CREATE TABLE, missing column list or select statement.')

      # as <select> version
      if tokens[0].get_value() == 'as':
         tokens = tokens[1:]
         if not tokens or tokens[0].get_value() != 'select':
            raise ValueError('Wrong syntax for CREATE TABLE, missing select statement.')
         tokens = tokens[1:]

         (_, columns_list, tables_list, condition) = self.select(tokens)
         return ('create_table_as', table_name, columns_list, tables_list, condition)

      # normal version
      # eats '(' token
      if tokens[0].get_value() != '(':
         raise ValueError('Wrong syntax for CREATE TABLE, expecting column list, got something else.')
      tokens = tokens[1:]

      column_names = []
      column_types = []
      i = 1
      while True:
         # eats column_name token
         if not tokens or tokens[0].get_name() != 'LITERAL':
            raise ValueError('Wrong syntax for CREATE TABLE, missing column entry number {}.'.format(i))
         if not self.name_regex.match(tokens[0].get_value()):
            raise ValueError('Wrong syntax for CREATE TABLE, column_name number {} contains forbidden characters.'.format(i))
         column_name = tokens[0].get_value()
         column_names.append(column_name)
         tokens = tokens[1:]

         # eats column_type token
         if not tokens or tokens[0].get_name() != 'TYPE':
            raise ValueError('Wrong syntax for CREATE TABLE, missing column_type after column_name number {}.'.format(i))
         column_type = tokens[0].get_value()
         column_types.append(column_type)
         tokens = tokens[1:]

         # eats separator token
         if not tokens or tokens[0].get_name() != 'SEPARATOR':
            raise ValueError('Wrong syntax for CREATE TABLE, missing separator after column entry number {}.'.format(i))
         if tokens[0].get_value() == ')':
            tokens = tokens[1:]
            break
         if tokens[0].get_value() != ',':
            raise ValueError('Wrong syntax for CREATE TABLE, wrong ( character inside columns list.')
         tokens = tokens[1:]
         i += 1

      # checks if all the tokens have been eaten
      if tokens:
         raise ValueError('Wrong syntax for CREATE TABLE, command doesn\'t end after )')

      return ('create_table', table_name, column_names, column_types)


   def print_table(self, tokens):
      # eats table_name token
      if not tokens:
         raise ValueError('Wrong syntax for PRINT, missing table_name.')
      if tokens[0].get_name() != 'LITERAL':
         raise ValueError('Wrong syntax for PRINT, table_name is a reserved keyword.')
      if not self.name_regex.match(tokens[0].get_value()):
         raise ValueError('Wrong syntax for PRINT, table_name contains forbidden characters.')
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # checks if all the tokens have been eaten
      if tokens:
         raise ValueError('Wrong syntax for PRINT, command doesn\'t end after table_name.')

      return ('print_table', table_name)


   def insert_into(self, tokens):
      # eats into token
      if not tokens or tokens[0].get_value() != 'into':
         raise ValueError('Wrong syntax for INSERT INTO, missing into after insert.')
      tokens = tokens[1:]

      # eats table_table token
      if not tokens:
         raise ValueError('Wrong syntax for INSERT INTO, missing table_name.')
      if tokens[0].get_name() != 'LITERAL':
         raise ValueError('Wrong syntax for INSERT INTO, table_name is a reserved keyword.')
      if not self.name_regex.match(tokens[0].get_value()):
         raise ValueError('Wrong syntax for INSERT INTO, table_name contains forbidden characters.')
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # eats values token
      if not tokens or tokens[0].get_value() != 'values':
         raise ValueError('Wrong syntax for INSERT INTO, missing values after table_name.')
      tokens = tokens[1:]

      values_list = []
      i = 1
      while True:
         # we're always expecting a value token because we either just started or we've eaten a separator token
         if not tokens:
            raise ValueError('Wrong syntax for INSERT INTO, missing expected value entry number {}.'.format(i))
         if tokens[0].get_name() == 'LITERAL':
            value = tokens[0].get_value()
            tokens = tokens[1:]
         else:
            raise ValueError('Wrong syntax for INSERT INTO, missing value entry number {}.'.format(i))
         values_list.append(value)

         # stops parsing if tokens are over
         if not tokens:
            return ('insert_into', table_name, values_list)

         # eats separator tokens if tokens aren't over
         if tokens[0].get_name() != 'SEPARATOR':
            raise ValueError('Wrong syntax for INSERT INTO, missing separator after value in entry number {}.'.format(i))
         if tokens[0].get_value() != ',':
            raise ValueError('Wrong syntax for INSERT INTO, expecting , got something else.')
         tokens = tokens[1:]
         i += 1

      # this code can't be executed
      raise ValueError('Something went wrong while parsing an INSERT INTO command.')


   def drop_table(self, tokens):
      # eats table_name token
      if not tokens:
         raise ValueError('Wrong syntax for DROP, missing table_name.')
      if tokens[0].get_name() != 'LITERAL':
         raise ValueError('Wrong syntax for DROP, table_name is a reserved keyword.')
      if not self.name_regex.match(tokens[0].get_value()):
         raise ValueError('Wrong syntax for DROP, table_name contains forbidden characters.')
      table_name = tokens[0].get_value()
      tokens = tokens[1:]

      # checks if all the tokens have been eaten
      if tokens:
         raise ValueError('Wrong syntax for DROP, command doesn\'t end after table_name.')

      return ('drop_table', table_name)


   def select(self, tokens):
      if not tokens:
         raise ValueError('Wrong syntax for SELECT, missing columns list.')

      # columns_list will remain empty only if * is specified instead of a columns list
      columns_list = []
      if tokens[0].get_value() == '*':
         tokens = tokens[1:]
      else:
         i = 0
         while True:
            # we're always expecting a column_name token because we either just started or we've eaten a separator token
            if not tokens:
               raise ValueError('Wrong syntax for SELECT, expecting column_name.')

            # eats column_name token
            if tokens[0].get_name() != 'LITERAL':
               raise ValueError('Wrong syntax for SELECT, missing column name number {}.'.format(i))

            columns_list.append(tokens[0].get_value())
            tokens = tokens[1:]

            # stops parsing if we don't find a separator token
            if not tokens:
               raise ValueError('Wrong syntax for SELECT, missing FROM clause')
            if tokens[0].get_name() != 'SEPARATOR':
               break

            # we eat the separator token and go on parsing the column_list
            tokens = tokens[1:]
            i += 1

      # eats from token
      if tokens[0].get_value() != 'from':
         raise ValueError('Wrong syntax for SELECT, missing FROM clause')
      tokens = tokens[1:]

      i = 0
      tables_list = []
      while True:
         # we're always expecting a table_name token because we either just started or we've eaten a separator token
         # and we discarded the * token case
         if not tokens:
            raise ValueError('Wrong syntax for SELECT, missing table name number {}.'.format(i))

         # eats table_name token
         if tokens[0].get_name() != 'LITERAL':
            raise ValueError('Wrong syntax for SELECT, missing column name number {}.'.format(i))

         tables_list.append(tokens[0].get_value())
         tokens = tokens[1:]

         # the where clause is optional
         if not tokens:
            return ('select', columns_list, tables_list, [])

         if tokens[0].get_name() != 'SEPARATOR':
            break

         tokens = tokens[1:]
         i += 1

      # eats where token
      if tokens[0].get_value() != 'where':
         raise ValueError('Wrong syntax for SELECT, expecting where clause after tables list.')
      tokens = tokens[1:]

      condition = self.infix_to_postfix(tokens)

      return ('select', columns_list, tables_list, condition)


   # shunting-yard algorithm without brackets support
   def infix_to_postfix(self, infix_tokens):
      if not infix_tokens:
            raise ValueError('Wrong syntax for SELECT, missing list of conditions.')

      operators_stack = []
      postfix_tokens = []
      for token in infix_tokens:
         # the token is a literal (column_name or a number/string)
         if token.get_name() == 'LITERAL':
            postfix_tokens.append(token.get_value())
            continue

         if token.get_name() != 'OPERATOR':
            raise ValueError('Wrong syntax for SELECT, expecting an operator, got something else.')

         # the token is an operator
         while True:
            if not operators_stack:
               break

            stack_head_operator = operators_stack[-1]
            stack_head_operator_priority = self.operators_priority[stack_head_operator]
            current_operator = token.get_value()
            current_operator_priority = self.operators_priority[current_operator]

            if stack_head_operator_priority < current_operator_priority:
               break

            postfix_tokens.append(operators_stack.pop())
         operators_stack.append(token.get_value())

      # there might still be something in the operator stack after the infix_tokens are finished
      while operators_stack:
         postfix_tokens.append(operators_stack.pop())

      return postfix_tokens