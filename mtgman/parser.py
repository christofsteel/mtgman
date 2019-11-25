from ply import lex, yacc
from .filter import findFilterClass, Conjunction, Disjunction, Name, Negation

tokens = ('NEGATION', "OR", "AND", "IDENT", "DIVIDER", "LPAREN", "RPAREN", "EXACT")

t_NEGATION = r'-'
def t_OR(t):
    r'\s(or|OR|Or|oR)\s'
    return t
t_IDENT = r'([\w]+|\"[\w\s]+\")+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EXACT = r'!'
t_DIVIDER = ':|>=|<=|!=|=|<|>'
t_AND = r'\s'


def t_error( t ):
  print("Invalid Token:",t.value[0])
  t.lexer.skip( 1 )

lexer = lex.lex()

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NEGATION'),
    ('nonassoc', 'DIVIDER'),
    ('nonassoc', 'IDENT'),
)


def p_querytoken(p):
    '''expr : IDENT DIVIDER IDENT'''
    try:
        p[0] = findFilterClass(p[1])(p[3],operand=p[2])
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
    p[0] = Disjunction(p[1], p[3])

def p_and(p):
    '''expr : expr AND expr'''
    p[0] = Conjunction(p[1], p[3])

def p_paren(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = p[2]

def p_exactname(p):
    '''expr : EXACT IDENT'''
    p[0] = Name(p[1], exact=True)

def p_exactfilter(p):
    '''expr : EXACT IDENT DIVIDER IDENT'''
    try:
        p[0] = findFilterClass(p[1])(p[3],operand=p[2], exact=True)
    except:
        p[0] = Name(p[1] + p[2] + p[3], exact=True)


parser = yacc.yacc()
