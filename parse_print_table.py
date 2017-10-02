import unittest
import src.lexer
import src.parser


class ParsePrintTable(unittest.TestCase):

   forbidden_table_names = (
      "print create",
      "print load",
      "print store",
      "print drop",
      "print insert",
      "print print",
      "print select",
      "print table",
      "print as",
      "print into",
      "print from",
      "print where",
      "print int",
      "print float",
      "print string"
   )


   spelling_errors = (
      "",
      "Print Test",
      "prints Test",
      "pritn Test"
   )


   trailing_stuff = (
      "print Test ddd",
      "print Test , stuff"
   )


   def test_forbidden_table_names(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.forbidden_table_names:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_spelling_errors(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.spelling_errors:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)


   def test_trailing_stuff(self):
      lexer = src.lexer.SQLLexer()
      parser = src.parser.SQLParser()
      for query in self.trailing_stuff:
         tokens = lexer.tokenize(query)
         self.assertRaises(ValueError, parser.parse, tokens)



if __name__ == '__main__':
   unittest.main()