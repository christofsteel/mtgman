import ply

class Token:    
    key = None
    allkeys = []

    def __init__(self, value, operand=":", exact=False):
        self.value = value
        self.op = operand
        self.exact = "!" if exact else ""

    def filter(self, card):
        raise NotImplementedError

    def __str__(self):
        return "{key}{op}{value}".format(key=self.key, value=self.value, op=self.op)

class Name(Token):
    def __str__(self):
        return "{exact}{value}".format(key=self.key, exact=self.exact, value=self.value, op=self.op)

class Paren:
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return "({ex})".format(ex=self.ex)

class Negation:
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return "-{ex}".format(ex = self.ex)

class Disjunction:
    def __init__(self, ex1, ex2):
        self.ex1 = ex1
        self.ex2 = ex2

    def filter(self, card):
        return self.ex1.filter(card) or self.ex2.filter(card)

    def __str__(self):
        return "({ex1} or {ex2})".format(ex1=self.ex1, ex2=self.ex2)

class Conjunction:
    def __init__(self, ex1, ex2):
        self.ex1 = ex1
        self.ex2 = ex2

    def filter(self, card):
        return self.ex1.filter(card) and self.ex2.filter(card)

    def __str__(self):
        return "{ex1} {ex2}".format(ex1=self.ex1, ex2=self.ex2)


list_of_tokens = [
        ["c","color"],
        ["id","identity"],
        ["has"],
        ["is"],
        ["t","type"],
        ["o","oracle"],
        ["fo"],
        ["m","mana"],
        ["cmc"],
        ["pow","power"],            
        ["tou","toughness"],            
        ["pt","powtou"],            
        ["loy","loyality"],            
        ["include"],            
        ["r","rarity"],            
        ["new"],            
        ["s","set","e","edition"],            
        ["cn","mumber"],            
        ["b","block"],            
        ["st"],            
        ["cube"],            
        ["f","format"],            
        ["banned"],
        ["restricted"],
        ["usd"],            
        ["tix"],            
        ["eur"],            
        ["a","art","artist"],            
        ["ft","flavor"], 
        ["wm","watermark"], 
        ["illustrations"], 
        ["border"], 
        ["frame"], 
        ["game"], 
        ["year"], 
        ["date"], 
        ["papersets"],
        ["lang", "language"],
        ]

tokenClasses = {l[0]: 
        type("tokenClass_%s" % l, (Token,), {"key": l[0], "allkeys":l})
        for l in list_of_tokens}

def findClass(s):
    for l in list_of_tokens:
        c = l[0]
        for j in l:
            if s == j:
                return tokenClasses[c]

