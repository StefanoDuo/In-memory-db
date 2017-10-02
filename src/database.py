from collections import OrderedDict
import itertools
import re



def zip_equal(*args):
   sentinel = None
   for combo in itertools.zip_longest(*args):
      if sentinel in combo:
         raise ValueError('You need to specify a new position for every column.')
      yield combo



# TODO: implement NaN and NOVALUE logic
class TypeString:
   regex = re.compile(r"^'.*'$")


   def __init__(self, value):
      if type(value) is str and not self.regex.match(value):
         raise TypeError("Value can't be parsed as a string.")
      self.is_NOVALUE = False
      self.value = str(value[1:-1])


   def get_value(self):
      return self.value


   def __str__(self):
      if self.is_NOVALUE:
         return "''"
      return "'" + self.get_value() + "'"


   def __add__(self, str2):
      return TypeString(self.get_value() + str2.get_value())


   def __lt__(self, str2):
      return self.get_value() < str2.get_value()


   def __le__(self, str2):
      return self.get_value() <= str2.get_value()


   def equal(self, str2):
      return self.get_value() == str2.get_value()


   def __ne__(self, str2):
      return self.get_value() != str2.get_value()


   def __gt__(self, str2):
      return self.get_value() > str2.get_value()


   def __ge__(self, str2):
      return self.get_value() >= str2.get_value()


   def boolean_and(self, str2):
      return bool(self.get_value()) and bool(str2.get_value())


   def boolean_or(self, str2):
      return bool(self.get_value()) or bool(str2.get_value())


   def operation(self, operator, str2):
      return self.operators[operator](self, str2)


   operators = {'+': __add__,
                '<': __lt__,
                '<=': __le__,
                '=': equal,
                '<>': __ne__,
                '>': __gt__,
                '>=': __ge__,
                'and': boolean_and,
                'or': boolean_or}



class TypeInt:
   regex = re.compile(r"^-?\d*$")


   def __init__(self, value):
      if type(value) is str and not self.regex.match(value):
         raise TypeError("Value can't be parsed as an int.")
      self.is_NaN = False
      self.is_NOVALUE = False
      self.value = int(value)


   def get_value(self):
      return self.value


   def __str__(self):
      if self.is_NaN:
         return "NaN"
      if self.is_NOVALUE:
         return "0"
      return str(self.get_value())


   def __add__(self, int2):
      return TypeInt(self.get_value() + int2.get_value())


   def __sub__(self, int2):
      return TypeInt(self.get_value() - int2.get_value())


   def __mul__(self, int2):
      return TypeInt(self.get_value() * int2.get_value())


   def __div__(self, int2):
      return TypeInt(self.get_value() / int2.get_value())


   def __lt__(self, int2):
      return self.get_value() < int2.get_value()


   def __le__(self, int2):
      return self.get_value() <= int2.get_value()


   def equal(self, int2):
      return self.get_value() == int2.get_value()


   def __ne__(self, int2):
      return self.get_value() != int2.get_value()


   def __gt__(self, int2):
      return self.get_value() > int2.get_value()


   def __ge__(self, int2):
      return self.get_value() >= int2.get_value()


   def operation(self, operator, str2):
      return self.operators[operator](self, str2)


   operators = {'+': __add__,
                '-': __sub__,
                '*': __mul__,
                '/': __div__,
                '<': __lt__,
                '<=': __le__,
                '=': equal,
                '<>': __ne__,
                '>': __gt__,
                '>=': __ge__}



class TypeFloat:
   regex = re.compile(r"^-?\d*\.\d*$")


   def __init__(self, value):
      if type(value) is str and not self.regex.match(value):
         raise TypeError("Value can't be parsed as a float.")
      self.is_NaN = False
      self.is_NOVALUE = False
      self.value = float(value)


   def get_value(self):
      return self.value


   def __str__(self):
      if self.is_NaN:
         return "NaN"
      if self.is_NOVALUE:
         return "0.0"
      return str(self.value)


   def __add__(self, float2):
      return TypeFloat(self.value + float2.value)


   def __sub__(self, float2):
      return TypeFloat(self.value - float2.value)


   def __mul__(self, float2):
      return TypeFloat(self.value * float2.value)


   def __div__(self, float2):
      return TypeFloat(self.value / float2.value)


   def __add__(self, float2):
      return TypeString(self.get_value() + float2.get_value())


   def __lt__(self, float2):
      return self.get_value() < float2.get_value()


   def __le__(self, float2):
      return self.get_value() <= float2.get_value()


   def equal(self, float2):
      return self.get_value() == float2.get_value()


   def __ne__(self, float2):
      return self.get_value() != float2.get_value()


   def __gt__(self, float2):
      return self.get_value() > float2.get_value()


   def __ge__(self, float2):
      return self.get_value() >= float2.get_value()


   def operation(self, operator, str2):
      return self.operators[operator](self, str2)


   operators = {'+': __add__,
                '-': __sub__,
                '*': __mul__,
                '/': __div__,
                '<': __lt__,
                '<=': __le__,
                '=': equal,
                '<>': __ne__,
                '>': __gt__,
                '>=': __ge__}



class Row:
   def __init__(self, row):
      self.row = tuple(row)


   @classmethod
   def create_from_rows(cls, *args):
      rows = itertools.chain(*args)
      return cls(rows)


   def verify_condition(self, condition):
      stack = []
      for element in condition:
         if element[0] == 'OPERATOR':
            operator = element[1]
            # try:
            arg2 = stack.pop()
            arg1 = stack.pop()
            # except IndexError as ie:
               # raise ValueError("Wrong syntax for SELECT, something went wrong while parsing the condition list.") from ie
            result = arg1.operation(operator, arg2)   #TODO: implement method operation for type class
            stack.append(result)
         elif element[0] == 'COLUMN_NAME':
            stack.append(self.row[element[1]])
         else:
            stack.append(element[1])
      return bool(stack.pop())


   def __getitem__(self, key):
      return self.row[key]


   def __str__(self):
      stringified_values = (str(value) for value in self.row)
      return ','.join(stringified_values)


   def __iter__(self):
      return iter(self.row)



class Table:
   def __init__(self, column_names_list, column_types_list):
      self.column_names = tuple(column_names_list)
      self.column_types = tuple(column_types_list)
      self.name_to_index = {column_name: index for index, column_name in enumerate(self.column_names)}
      self.rows = []


   @classmethod
   def cartesian_product(cls, tables):
      names_iter = (col_name for table in tables for col_name in table.get_column_names())
      types_iter = (col_type for table in tables for col_type in table.get_column_types())
      table_object = cls(names_iter, types_iter)
      row_groups = list(table.get_rows() for table in tables)
      cartesian_product = itertools.product(*row_groups) # each entry will be a tuple of rows
      new_rows = (Row.create_from_rows(*row) for row in cartesian_product) # we merge each tuple of rows into a single row
      for row in new_rows:
         table_object.insert_row(row)
      return table_object


   def extract_columns_by_index(self, column_indexes):
      filter_iterator = tuple(i in column_indexes for i in range(len(self.column_names)))
      column_names = itertools.compress(self.column_names, filter_iterator)
      column_types = itertools.compress(self.column_types, filter_iterator)
      filtered_table = Table(column_names, column_types)
      filtered_rows = (itertools.compress(row, filter_iterator) for row in self.get_rows())
      for row in filtered_rows:
         filtered_table.insert_row(row)
      return filtered_table


   def extract_columns_by_name(self, column_names):
      indexes = tuple(self.get_index_by_name(column_name) for column_name in column_names)
      return self.extract_columns_by_index(indexes)


   def reorder_iterable(self, order, it):
      zipped_it = zip_equal(order, it)
      ordered_it = sorted(zipped_it)
      return (el[1] for el in ordered_it)


   def reorder_columns(self, order):
      ordered_column_names = self.reorder_iterable(order, self.column_names)
      ordered_column_types = self.reorder_iterable(order, self.column_types)

      reordered_table = Table(ordered_column_names, ordered_column_types)
      ordered_rows = (self.reorder_iterable(order, row) for row in self.get_rows())
      for row in ordered_rows:
         row = list(row)
         reordered_table.insert_row(row)
      return reordered_table


   def filter_table(self, condition):
      if not condition:
         return self
      condition = self.modify_condition(condition)
      filtered_table = Table(self.get_column_names(), self.get_column_types())
      for row in self.get_rows():
         if row.verify_condition(condition):
            filtered_table.insert_row(row)
      return filtered_table


   # this can't be done by the parser because it needs to know about tables etc.
   def modify_condition(self, condition):
      modified_condition = []
      column_names = self.get_column_names()
      for element in condition:
         if element in column_names:
            modified_condition.append(('COLUMN_NAME', self.get_index_by_name(element)))
         elif TypeFloat.regex.match(element):
            modified_condition.append(('LITERAL', TypeFloat(element)))
         elif TypeInt.regex.match(element):
            modified_condition.append(('LITERAL', TypeInt(element)))
         elif TypeString.regex.match(element):
            modified_condition.append(('LITERAL', TypeString(element)))
         else:
            modified_condition.append(('OPERATOR', element))
      return modified_condition


   def __str__(self):
      table_header = self.get_header_string()
      stringified_rows = (str(row) for row in self.get_rows())
      table_content = '\n'.join(stringified_rows)
      return table_header + '\n' + table_content


   def insert_row(self, row):
      self.rows.append(Row(row))


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
   value_parse = {'string': TypeString,
                  'float': TypeFloat,
                  'int': TypeInt}


   def __init__(self):
      self.tables = {}


   def transact(self, command, *args):
      return self.commands[command](self, *args)


   def create_table(self, table_name, column_names, column_types):
      if table_name in self.tables:
         raise NameError('A table named {} doesn\'t exists in memory.'.format(table_name))

      self.tables[table_name] = Table(column_names, column_types)


   def print_table(self, table_name):
      if table_name not in self.tables:
         raise NameError('A table named {} doesn\'t exists in memory.'.format(table_name))

      table = self.tables[table_name]
      return str(table)


   def drop_table(self, table_name):
      if table_name not in self.tables:
         raise NameError('A table named {} doesn\'t exists in memory.'.format(table_name))

      del self.tables[table_name]


   def insert_into(self, table_name, values_list):
      if table_name not in self.tables:
         raise NameError('A table named {} doesn\'t exists in memory.'.format(table_name))

      table = self.tables[table_name]
      types = table.get_column_types()
      parsed_values = []
      for i, (value, column_type) in enumerate(itertools.zip_longest(values_list, types)):
         if not column_type or not value:
            raise ValueError('There are too many values in the values list.')
         try:
            value = self.value_parse[column_type](value)
         except TypeError:
            raise TypeError("Value number {} isn't of type {}".format(i, column_type))
         parsed_values.append(value)

      table.insert_row(parsed_values)


   # TODO: implement filtering applying condition to every row
   def select(self, columns_list, tables_list, condition):
      # checks if all the tables exist and creates the tables scope
      tables_scope = {}
      for table_name in tables_list:
         if table_name not in self.tables:
            raise NameError('A table named {} doesn\'t exists in memory.'.format(table_name))
         tables_scope[table_name] = self.tables[table_name]

      if not columns_list:
         columns_list = list(column for table in tables_scope.values() for column in table.get_column_names())

      # checks if all the columns_name exist in the tables scope, and stores their position in the select table
      columns = OrderedDict()
      for i, column_name in enumerate(columns_list):
         if column_name in columns: # at the moment we only support columns with distinct names
            raise ValueError('You can\'t have 2 columns with the same name in a query.')
         for table_name, table in tables_scope.items():
            if column_name in table.get_column_names():
               columns[column_name] = i
               break
         else: # executes only if the for loop terminates by exhaustion (not with a break)
            raise NameError('A column named {} doesn\'t exists inside the specified tables list.'.format(column_name))

      select_table = Table.cartesian_product(tables_scope.values())

      select_table = select_table.filter_table(condition)

      column_names_iterator = (column_name for column_name in columns)
      select_table = select_table.extract_columns_by_name(column_names_iterator)

      columns_order = tuple(columns[column_name] for column_name in select_table.get_column_names())
      select_table = select_table.reorder_columns(columns_order)

      return str(select_table)


   commands = {'create_table': create_table,
               'drop_table': drop_table,
               'insert_into': insert_into,
               'print_table': print_table,
               'select': select}