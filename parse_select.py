import unittest
import src.lexer
import src.parser


class ParseSelect(unittest.TestCase):

   forbidden_table_names = (
      "select column_name from create",
      "select column_name from load",
      "select column_name from store",
      "select column_name from drop",
      "select column_name from insert",
      "select column_name from print",
      "select column_name from select",
      "select column_name from table",
      "select column_name from as",
      "select column_name from into",
      "select column_name from from",
      "select column_name from where",
      "select column_name from int",
      "select column_name from float",
      "select column_name from string"
   )


   spelling_errors = (
      "",
      "Select * from Test",
      "select * From Test",
      "selects * from Test",
      "select * froms Test",
      "seleect * from Test",
      "select * form Test"
   )


   column_list_errors = (
      # "select *, column_name from Test",
      "select column_name1, from Test",
      "select column_name1 column_name2 from Test",
      "select column_name1, , column_name2 from Test",
      "select , column_name2 from Test"
      "select , column_name2, column_name3 from Test"
   )


   table_list_errors = (
      "select column_name from Test,",
      "select column_name from Test1 Test2",
      "select column_name from Test1, , Test3",
      "select column_name from , Test2",
      "select column_name from , Test2, Test3"
   )


   trailing_stuff = (
      "select * from Teststuff",
      "insert into Test ...,,",
   )


   def test_forbidden_table_names(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.forbidden_table_names:
         tokens = lexer.tokenize(query)
         self.assertRaises(ParseError, parser.parse, tokens)


   def test_spelling_errors(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.spelling_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ParseError, parser.parse, tokens)


   def test_column_list_errors(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.column_list_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ParseError, parser.parse, tokens)


   def test_table_list_errors(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.table_list_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ParseError, parser.parse, tokens)


   def test_trailing_stuff(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.trailing_stuff:
         tokens = lexer.tokenize(query)
         self.assertRaises(ParseError, parser.parse, tokens)


if __name__ == '__main__':
   unittest.main()