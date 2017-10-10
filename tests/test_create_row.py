import unittest
import itertools
import context
from context import sql_interpreter
import sql_interpreter.database



class CreateRow(unittest.TestCase):

   rows = (
      (1, 2, 3),
      (1., 2., 3.),
      ("1", "2", "3")
   )


   def test_create_row_from_values(self):
      for value_tuple in self.rows:
         row = sql_interpreter.database.Row(value_tuple)
         for i, value in enumerate(value_tuple):
            self.assertEqual(row[i], value)
         for tuple in zip(row, value_tuple):
            self.assertEqual(*tuple)



if __name__ == '__main__':
   unittest.main()