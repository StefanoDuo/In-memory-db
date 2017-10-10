import unittest
from context import sql_interpreter
import sql_interpreter.lexer
import sql_interpreter.parser


class ParseInsertInto(unittest.TestCase):

   forbidden_table_names = (
      "insert into create 1,2,3",
      "insert into load 1,2,3",
      "insert into store 1,2,3",
      "insert into drop 1,2,3",
      "insert into insert 1,2,3",
      "insert into print 1,2,3",
      "insert into select 1,2,3",
      "insert into table 1,2,3",
      "insert into as 1,2,3",
      "insert into into 1,2,3",
      "insert into from 1,2,3",
      "insert into where 1,2,3",
      "insert into int 1,2,3",
      "insert into float 1,2,3",
      "insert into string 1,2,3"
   )

   spelling_errors = (
      "",
      "Insert into Test (column_name int)",
      "insert Into Test (column_name int)",
      "inserts into Test (column_name int)",
      "insert intos Test (column_name int)",
      "insetr into Test (column_name int)",
      "insert intro Test (column_name int)"
   )

   values_list_errors = (
      "insert into Test",
      "insert into Test 1,",
      "insert into Test 1, , 3",
      "insert into Test , 2",
      "insert into Test , 2, 3",
      "insert into Test 1 2 3",
      "insert into Test ,"
   )

   trailing_stuff = (
      "insert into Test 1, 2, 3 stuff",
      "insert into Test 1, 2, 3 ...,,",
   )

   def test_forbidden_table_names(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.forbidden_table_names:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_spelling_errors(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.spelling_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_values_list_errors(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.values_list_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_trailing_stuff(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.trailing_stuff:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


if __name__ == '__main__':
   unittest.main()