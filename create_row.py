import unittest
import src.database
import itertools



class CreateRow(unittest.TestCase):

   rows = (
      (1, 2, 3),
      (1., 2., 3.),
      ("1", "2", "3")
   )


   def test_create_row_from_values(self):
      for value_tuple in self.rows:
         row = src.database.Row(value_tuple)
         for i, value in enumerate(value_tuple):
            self.assertEqual(row[i], value)
         for tuple in zip(row, value_tuple):
            self.assertEqual(*tuple)


   def test_create_row_from_rows(self):
      rows = [src.database.Row(value_tuple) for value_tuple in self.rows]
      row = src.database.Row.create_from_rows(*rows)
      self.assertEqual(type(row),)
      for tuple in zip(row, itertools.chain(*rows)):
         self.assertEqual(*tuple)



if __name__ == '__main__':
   unittest.main()