from ply import lex

tokens = ('NEGATION', "IDENT", "DIVIDER", "OR", "LPAREN", "RPAREN", "QUOTE")

t_NEGATION = r'-'
t_IDENT = r'[\w\s]+'
t_OR = r'or|OR|Or|oR'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_QUOTE = "\""
t_DIVIDER = ':|>|<|=|>=|<=|!='

lexer = lex.lex()
