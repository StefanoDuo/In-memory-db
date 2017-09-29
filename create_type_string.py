import unittest
import src.database



class CreateTypeString(unittest.TestCase):

   correct_values = (
      "'this is a string'",
   )


   wrong_values = (
      "this is not a string",
      "3.2",
      "2.",
      ".3",
      ".",
      "-3.2",
      "-2.",
      "-.3",
      "-.",
      "1",
      "-3"
   )


   def test_correct_values(self):
      for value in self.correct_values:
         result = src.database.TypeString(value)
         result = str(result)
         self.assertEqual(result, value)


   def test_wrong_values(self):
      for value in self.wrong_values:
         self.assertRaises(TypeError, src.database.TypeString, value)



if __name__ == '__main__':
   unittest.main()