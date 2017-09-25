import db.lexer
import db.parser
import db.database


def print_tokens(tokens):
   for token in tokens:
      print(token)



# TODO: implement a real test case
if __name__ == '__main__':
   lexer = db.lexer.SQLLexer()
   database = db.database.Database()
   parser = db.parser.SQLParser(database)

   if False:
      print('STARTING QUERY SYNTAX TEST')
      queries = ('create table Test ()',
                 'create tabsle Test (col1 int, col2 float, col3 string)',
                 'creates table Test (col1 int, col2 float, col3 string)',
                 'create tables Test (col1 int, col2 float, col3 string)',
                 'credate table Test (col1 int, col2 float, col3 string)',
                 'create table T(est int (col1 int, col2 float, col3 string)',
                 'create table Test (col1 ints, col2 float, col3 string)',
                 'create table Test (col1 int, col2 fldoat, col3 string)',
                 'create table Test (col1 int, col2 float, col3 strindg)',
                 'create table Test (col1 Int, col2 float, col3 string)',
                 'create table Test (col1 int, col2 Float, col3 string)',
                 'create table Test (col1 int, col2 float, col3 String)',
                 'create table Test (col1 int, col2 float, col3 string,)',
                 'create table Test (col1 int, col2 float, col3 string',
                 'create table Test (col1 int, col2 float, col3 string) :::',
                 'create table Test (c`ol1 int, col2 float col3 string)')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING CREATE TABLE TEST')
      queries = ['create table Test (c1 int, c2 int, c3 float)',
                 'create table Test2 (c11 int, c12 string, c13 float)',
                 'create table Test (c string)',
                 'create table Test2 (jjjj float)']
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         # print_tokens(tokens)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print create',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING INSERT TABLE TEST')
      queries = ('insert into Testd values 4,2,3.2',
                 'insert into Test values 0,\'strintest\',2',
                 'insert into Test values 0,1,2',
                 'insert into Test values 3,4,5',
                 'insert into Test values 6,7,8',
                 'insert into Test values 0,2,',
                 'insert into Test values 4,,3.2',
                 'insert into Test values 4,3,3.2, 4,22',
                 'insert into Test values 4,4',
                 'insert into Test2 values 0,\'Hello World!\',3.2',
                 'insert into Test2 values 1,\'Hello World!\',3.2',
                 'insert into Test2 values 2,\'Hello World!\',3.2',
                 'insert into Test2 values 3,\'Hello World!\',3.2',
                 'insert into Test2 values 4,\'Hello World!\',3.2')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print into as',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING DROP TABLE TEST')
      queries = ('drop Test',
                 'drop Test2',
                 'drop into as',
                 'drop   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if False:
      print('STARTING PRINT TABLE TEST')
      queries = ('print Test',
                 'print Test2',
                 'print into as',
                 'print   Test')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')

   if True:
      print('STARTING SELECT TABLE TEST')
      queries = ('select c3, c2, c1 from Test',
                 'select c1, c2, c3, c11 from Test, Test2')
      for query in queries:
         print(query)
         tokens = lexer.tokenize(query)
         result = parser.parse(tokens)
         print(result)
         print('------------------------------------------------')