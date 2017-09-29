import unittest
import src.database



class CreateTypeFloat(unittest.TestCase):

   correct_values = (
      "3.2",
      "2.",
      ".3",
      "."
   )


   wrong_values = (
      "'this is not a float'",
      "this is not a float",
      "2"
   )


   def test_correct_values(self):
      for value in self.correct_values:
         result = src.database.TypeFloat(value)
         result = str(result)
         self.assertEqual(result, value)


   def test_wrong_values(self):
      for value in self.wrong_values:
         self.assertRaises(TypeError, src.database.TypeFloat, value)



if __name__ == '__main__':
   unittest.main()