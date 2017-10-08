import unittest
import src.database



class CreateTypeInt(unittest.TestCase):

   correct_values = (
      "1",
      "-1",
   )


   wrong_values = (
      "'this is not an int'",
      "this is not an int",
      "3.2",
      "2.",
      ".3",
      ".",
      "-3.2",
      "-2.",
      "-.3",
      "-."
   )


   def test_correct_values(self):
      output = tuple(str(src.database.TypeInt(value)) for value in self.correct_values)
      self.assertSequenceEqual(output, self.correct_values)


   def test_wrong_values(self):
      for value in self.wrong_values:
         self.assertRaises(TypeError, src.database.TypeInt, value)



if __name__ == '__main__':
   unittest.main()