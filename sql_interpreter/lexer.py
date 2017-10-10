import re



class Token:
   def __init__(self, name, value):
      self.name = name
      self.value = value


   def get_name(self):
      return self.name


   def get_value(self):
      return self.value


   def __str__(self):
      return self.get_name() + ': ' + self.get_value()



# TODO: instead of returning a simple token list, create an object which has a next method for
# for every token type and keeps track internally of the token list
class SQLLexer:
   commands = {'create', 'load', 'store', 'drop', 'insert', 'print', 'select'}
   keywords = {'table', 'as', 'into', 'from', 'where'}
   types = {'string', 'int', 'float'}
   operators = {'and', 'or', '>', '<', '=', '=>', '<=', '-', '+', '*', '/'}
   list_separator = {',', '(', ')'} # TODO: move , and () into different sets


   split_maintaining = {',', '(', ')'}
   split_discarding = {'\n', '\t', ' '}


   def token(self, token_value):
      if token_value in self.commands:
         token_name = 'COMMAND'
      elif token_value in self.keywords:
         token_name = 'KEYWORD'
      elif token_value in self.list_separator:
         token_name = 'SEPARATOR'
      elif token_value in self.types:
         token_name = 'TYPE'
      elif token_value in self.operators:
         token_name = 'OPERATOR'
      else:
         token_name = 'LITERAL'
      return Token(token_name, token_value)


   def tokenize(self, string):
      inside_string = False
      t_start = 0
      t_end = -1  # needed for empty string checking
      tokens = []
      for t_end, character in enumerate(string):
         if character == "'":
            inside_string = not inside_string
         elif not inside_string and character in self.split_discarding:
            if t_start == t_end:
               # if we find a discarding_split_character at the start of the string or after we just split
               # we ignore it because there's nothing to split
               t_start += 1
            else:
               # otherwise we append what is inside the interval [t_start, t_end) and move on
               tokens.append(self.token(string[t_start:t_end]))
               t_start = t_end + 1
         elif not inside_string and character in self.split_maintaining:
            if t_start != t_end:
               # if we find a maintaining_splitcharacter at the start of the string or after we just split
               # we append it and move on without append anything else
               tokens.append(self.token(string[t_start:t_end]))
            tokens.append(self.token(character))
            t_start = t_end + 1
      if t_start <= t_end:
         tokens.append(self.token(string[t_start:t_end+1]))
      return tokens