import unittest
from context import sql_interpreter
import sql_interpreter.lexer
import sql_interpreter.parser


class ParseDropTable(unittest.TestCase):

   forbidden_table_names = (
      "drop create",
      "drop load",
      "drop store",
      "drop drop",
      "drop insert",
      "drop print",
      "drop select",
      "drop table",
      "drop as",
      "drop into",
      "drop from",
      "drop where",
      "drop int",
      "drop float",
      "drop string"
   )


   spelling_errors = (
      "",
      "Drop Test",
      "drops Test",
      "dorp Test"
   )


   trailing_stuff = (
      "drop Test ddd",
      "drop Test , stuff"
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

   
   def test_trailing_stuff(self):
      lexer = sql_interpreter.lexer.SQLLexer()
      parser = sql_interpreter.parser.SQLParser()
      for query in self.trailing_stuff:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)



if __name__ == '__main__':
   unittest.main()