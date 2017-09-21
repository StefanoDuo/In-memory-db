from collections import OrderedDict
import itertools
import re


# TODO: implement base class for shared methods between Type classes
class TypeString:
   regex = re.compile(r"^'.*'$")

   def __init__(self, string):
      if not self.regex.match(string):
         raise TypeError("Value can't be parsed as a string.")
      self.is_NOVALUE = False
      self.value = string[1:-1]

   def __str__(self):
      if self.is_NOVALUE:
         return "''"
      return "'" + self.value + "'"



class TypeInt:
   regex = re.compile(r"^-?\d*$")

   def __init__(self, int):
      if not self.regex.match(int):
         raise TypeError("Value can't be parsed as an int.")
      self.is_NaN = False
      self.is_NOVALUE = False
      self.value = int

   def __str__(self):
      if self.is_NaN:
         return "NaN"
      if self.is_NOVALUE:
         return "0"
      return str(self.value)



class TypeFloat:
   regex = re.compile(r"^-?\d*.\d*$")

   def __init__(self, float):
      if not self.regex.match(float):
         raise TypeError("Value can't be parsed as a float.")
      self.is_NaN = False
      self.is_NOVALUE = False
      self.value = float

   def __str__(self):
      if self.is_NaN:
         return "NaN"
      if self.is_NOVALUE:
         return "0.0"
      return str(self.value)



class Row:
   def __init__(self, row):
      self.row = tuple(row)

   def __getitem__(self, key):
      return self.row[key]

   def __str__(self):
      stringified_values = (str(value) for value in self.row)
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
   value_parse = {'string': TypeString,
                  'float': TypeFloat,
                  'int': TypeInt}

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
      for i, (value, column_type) in enumerate(itertools.zip_longest(values_list, types)):
         if not column_type:
            return 'There are too many values in the values list.'
         if not value:
            return 'There are too few values in the values list.'
         try:
            value = self.value_parse[column_type](value)
         except TypeError:
            return "Value number {} isn't of type {}".format(i, column_type)
         parsed_values.append(value)

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