import unittest
import itertools
from src.database import Table



class CreateTable(unittest.TestCase):

   column_names = (("c1", "c2", "c3"), ("c4", "c5"))
   column_types = (("int", "int", "int"), ("int", "int"))
   values = (((1, 2, 3), (4, 5, 6)), ((10, 11), (12, 13)))

   create_result = ("c1 int,c2 int,c3 int", "c4 int,c5 int")
   insert_result = ("c1 int,c2 int,c3 int\n1,2,3\n4,5,6", "c4 int,c5 int\n10,11\n12,13")
   cartesian_product_result = "c1 int,c2 int,c3 int,c4 int,c5 int\n1,2,3,10,11\n1,2,3,12,13\n4,5,6,10,11\n4,5,6,12,13"

   column_indexes_to_extract = ((1, 2), (1,))
   column_names_to_extract = (("c2", "c3"), ("c5",))
   extract_columns_result = ("c2 int,c3 int\n2,3\n5,6", "c5 int\n11\n13")

   columns_new_order = ((1, 2, 0), (0, 1))
   new_order_result = ("c3 int,c1 int,c2 int\n3,1,2\n6,4,5", "c4 int,c5 int\n10,11\n12,13")


   def test_create_table(self):
      output = [str(Table(names, types)) for names, types in zip(self.column_names, self.column_types)]
      self.assertSequenceEqual(output, self.create_result)

   def test_insert_into_table(self):
      empty_tables = [Table(names, types) for names, types in zip(self.column_names, self.column_types)]
      output = []
      for table, rows in zip(empty_tables, self.values):
         for row in rows:
            table.insert_row(row)
         output.append(str(table))
      self.assertSequenceEqual(output, self.insert_result)


   def test_cartesian_product(self):
      tables = [Table(names, types) for names, types in zip(self.column_names, self.column_types)]
      for table, rows in zip(tables, self.values):
         for row in rows:
            table.insert_row(row)
      cartesian_product = Table.cartesian_product(tables)
      self.assertEqual(str(cartesian_product), self.cartesian_product_result)


   def test_extract_columns_by_index(self):
      tables = [Table(names, types) for names, types in zip(self.column_names, self.column_types)]
      output = []
      for table, rows, indexes in zip(tables, self.values, self.column_indexes_to_extract):
         for row in rows:
            table.insert_row(row)
         extracted_table = table.extract_columns_by_index(indexes)
         output.append(str(extracted_table))
      self.assertSequenceEqual(output, self.extract_columns_result)


   def test_extract_columns_by_name(self):
      tables = [Table(names, types) for names, types in zip(self.column_names, self.column_types)]
      output = []
      for table, rows, names in zip(tables, self.values, self.column_names_to_extract):
         for row in rows:
            table.insert_row(row)
         extracted_table = table.extract_columns_by_name(names)
         output.append(str(extracted_table))
      self.assertSequenceEqual(output, self.extract_columns_result)


   def test_reorder_columns(self):
      tables = [Table(names, types) for names, types in zip(self.column_names, self.column_types)]
      output = []
      for table, rows, order in zip(tables, self.values, self.columns_new_order):
         for row in rows:
            table.insert_row(row)
         reordered_table = table.reorder_columns(order)
         output.append(str(reordered_table))
      self.assertSequenceEqual(output, self.new_order_result)



if __name__ == '__main__':
   unittest.main()