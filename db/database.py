from collections import OrderedDict
import itertools
import re



def zip_equal(*args):
   sentinel = None
   for combo in itertools.zip_longest(*args):
      if sentinel in combo:
         raise ValueError('You need to specify a new position for every column.')
      yield combo



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

   @classmethod
   def create_from_rows(cls, *args):
      rows = itertools.chain(*args)
      return cls(rows)

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
      names_iter = (name for table in tables for name in table.get_column_names())
      types_iter = (col_type for table in tables for col_type in table.get_column_types())
      table_object = cls(names_iter, types_iter)
      row_groups = list(table.get_rows() for table in tables)
      cartesian_product = itertools.product(*row_groups) # will contain tuples of rows
      new_rows = (Row.create_from_rows(*row) for row in cartesian_product)
      for row in new_rows:
         table_object.insert_row(row)
      return table_object


   def extract_columns_by_index(self, column_indexes):
      column_indexes = tuple(column_indexes)
      filter_iterator = [i in column_indexes for i in range(len(self.column_names))]
      column_names = itertools.compress(self.column_names, filter_iterator)
      column_types = itertools.compress(self.column_types, filter_iterator)
      filtered_table = Table(column_names, column_types)
      filtered_rows = (itertools.compress(row, filter_iterator) for row in self.get_rows())
      for row in filtered_rows:
         filtered_table.insert_row(row)
      return filtered_table


   def extract_columns_by_name(self, column_names):
      indexes = (self.get_index_by_name(column_name) for column_name in column_names)
      return self.extract_columns_by_index(indexes)


   def reorder_iterable(self, order, it):
      zipped_it = zip_equal(order, it)
      ordered_it = sorted(zipped_it)
      return (el[1] for el in ordered_it)


   def reorder_columns(self, order):
      order = tuple(order)
      ordered_column_names = self.reorder_iterable(order, self.column_names)
      ordered_column_types = self.reorder_iterable(order, self.column_types)

      reordered_table = Table(ordered_column_names, ordered_column_types)
      ordered_rows = (self.reorder_iterable(order, row) for row in self.get_rows())
      for row in ordered_rows:
         row = list(row)
         reordered_table.insert_row(row)
      return reordered_table


   def __str__(self):
      table_header = self.get_header_string()
      stringified_rows = (str(row) for row in self.get_rows())
      table_content = '\n'.join(stringified_rows)
      return table_header + '\n' + table_content


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
   value_parse = {'string': TypeString,
                  'float': TypeFloat,
                  'int': TypeInt}


   def __init__(self):
      self.tables = {}


   def create_table(self, table_name, column_names, column_types):
      if table_name in self.tables:
         return 'A table named {} alredy exists in memory.'.format(table_name)

      self.tables[table_name] = Table(column_names, column_types)
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


   # TODO: * as column list logic
   def select(self, columns_list, tables_list):
      # checks if all the tables exist and creates the tables scope
      tables_scope = {}
      for table_name in tables_list:
         if table_name not in self.tables:
            return 'A table named {} doesn\'t exists in memory.'.format(table_name)
         tables_scope[table_name] = self.tables[table_name]

      # checks if all the columns_name exist in the tables scope, and stores info about every column
      columns = OrderedDict()
      for i, column_name in enumerate(columns_list):
         if column_name in columns: # at the moment we only support columns with distinct names
            return 'You can\'t have 2 columns with the same name in a query.'
         for table_name, table in tables_scope.items():
            if column_name in table.get_column_names():
               column_index = table.get_index_by_name(column_name)
               column_type = table.get_column_type_by_index(column_index)
               # using a dict to simplify properties access
               column_entry = {'old_index': column_index, 'new_index': i}
               columns[column_name] = column_entry
               break
         else: # executes only if the for loop terminates by exhaustion (not with a break)
            return 'A column named {} doesn\'t exists inside the specified tables list.'.format(column_name)

      select_table = Table.cartesian_product(tables_scope.values())

      column_names_iterator = (column_name for column_name in columns)
      select_table = select_table.extract_columns_by_name(column_names_iterator)

      columns_order = (columns[column_name]['new_index'] for column_name in select_table.get_column_names())
      select_table = select_table.reorder_columns(columns_order)
      return str(select_table)