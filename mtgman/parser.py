from ply import lex, yacc
from .scryfallsyntax import findClass, Conjunction, Disjunction, Name, Negation, Paren

tokens = ('NEGATION', "IDENT", "DIVIDER", "OR", "LPAREN", "RPAREN", "EXACT")

t_NEGATION = r'-'
t_IDENT = r'([\w]+|\"[\w\s]+\")+'
t_OR = r'or|OR|Or|oR'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EXACT = r'!'
t_DIVIDER = ':|>=|<=|!=|=|<|>'

t_ignore = r' '

def t_error( t ):
  print("Invalid Token:",t.value[0])
  t.lexer.skip( 1 )

lexer = lex.lex()

precedence = (
    ('right', 'NEGATION'),
    ('left', 'OR'),
    ('nonassoc', 'IDENT'),
)


def p_querytoken(p):
    '''expr : IDENT DIVIDER IDENT'''
    try:
        p[0] = findClass(p[1])(p[3],operand=p[2])
    except:
        p[0] = Name(p[1] + p[2] + p[3])

def p_neg(p):
    '''expr : NEGATION expr'''
    p[0] = Negation(p[2])

def p_cardname(p):
    '''expr : IDENT'''
    p[0] = Name(p[1])

def p_or(p):
    '''expr : expr OR expr'''
    p[0] = Disjunction(p[1], p[2])

def p_and(p):
    '''expr : expr expr'''
    p[0] = Conjunction(p[1], p[2])

def p_paren(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = Paren(p[2])

parser = yacc.yacc()
