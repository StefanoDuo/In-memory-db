import unittest
from context import sql_interpreter
import sql_interpreter.lexer
import sql_interpreter.parser



class ParseCreateTable(unittest.TestCase):

   forbidden_table_names = (
      "create table create (column_name int)",
      "create table load (column_name int)",
      "create table store (column_name int)",
      "create table drop (column_name int)",
      "create table insert (column_name int)",
      "create table print (column_name int)",
      "create table select (column_name int)",
      "create table table (column_name int)",
      "create table as (column_name int)",
      "create table into (column_name int)",
      "create table from (column_name int)",
      "create table where (column_name int)",
      "create table int (column_name int)",
      "create table float (column_name int)",
      "create table string (column_name int)"
   )

   forbidden_column_names = (
      "create table Test (create int)",
      "create table Test (load int)",
      "create table Test (store int)",
      "create table Test (drop int)",
      "create table Test (insert int)",
      "create table Test (print int)",
      "create table Test (select int)",
      "create table Test (table int)",
      "create table Test (as int)",
      "create table Test (into int)",
      "create table Test (from int)",
      "create table Test (where int)",
      "create table Test (int int)",
      "create table Test (float int)",
      "create table Test (string int)"
   )

   spelling_errors = (
      "",
      "Create table Test (column_name int)",
      "create Table Test (column_name int)",
      "creates table Test (column_name int)",
      "create tables Test (column_name int)",
      "creatr table Test (column_name int)",
      "create tablr Test (column_name int)",
      "create table Test (column_name Int)",
      "create table Test (column_name inte)",
      "create table Test (column_name ins)",
      "create table Test (column_name Float)",
      "create table Test (column_name floats)",
      "create table Test (column_name flaot)",
      "create table Test (column_name String)",
      "create table Test (column_name strings)",
      "create table Test (column_name stirng)"
   )

   column_list_errors = (
      "create table Test",
      "create table Test (column_name1)",
      "create table Test (int)",
      "create table Test (column_name int, )",
      "create table Test (column_name int, , column_name2 float)",
      "create table Test (column_name int column_name2 float)",
      "create table Test (column_name, column_name2 float)",
      "create table Test (column_name string, column_name2)",
      "create table Test (column_name string",
      "create table Test (column_name string,",
      "create table Test (column_name string, column_name2",
      "create table Test (column_name string, int"
   )

   trailing_stuff = (
      "create table Test (column_name float) stuff",
      "create table Test (column_name float), column_name2 float"
   )

   def test_forbidden_table_names(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.forbidden_table_names:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_forbidden_column_names(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.forbidden_column_names:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_spelling_errors(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.spelling_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_column_list_errors(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.column_list_errors:
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