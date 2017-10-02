import unittest
import src.database



class CreateTypeFloat(unittest.TestCase):

   correct_values = (
      "311.232",
      "3.2",
      "2.",
      ".3",
      "4.",
      ".6",
      "-311.232",
      "-3.2",
      "-2.",
      "-.3",
      "-4.",
      "-.6"
   )

   print_correct_value = (
      "311.232",
      "3.2",
      "2.0",
      "0.3",
      "4.0",
      "0.6",
      "-311.232",
      "-3.2",
      "-2.0",
      "-0.3",
      "-4.0",
      "-0.6"
   )


   wrong_values = (
      "'this is not a float'",
      "this is not a float",
      "2"
   )


   def test_correct_values(self):
      for value, print in zip(self.correct_values, self.print_correct_value):
         result = src.database.TypeFloat(value)
         result = str(result)
         self.assertEqual(result, print)


   def test_wrong_values(self):
      for value in self.wrong_values:
         self.assertRaises(TypeError, src.database.TypeFloat, value)



if __name__ == '__main__':
   unittest.main()