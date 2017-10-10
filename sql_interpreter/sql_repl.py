from src import lexer
from src import parser
from src import database


if __name__ == '__main__':
   lexer_ = lexer.SQLLexer()
   parser_ = parser.SQLParser()
   database_ = database.Database()

   while True:
      query = input('Waiting for a new query, write exit to stop.\n')
      if query == 'exit':
         break

      tokens = lexer_.tokenize(query)
      try:
         result = database_.transact(*parser_.parse(tokens))
         if result:
            print(result)
      except (NameError, ValueError, TypeError) as e:
         print(e)

      print()