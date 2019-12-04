import ply
from .model import Card
from sqlalchemy import and_, or_, not_

class Filter:    
    key = ""
    allkeys = []

    def __init__(self, value, operand="", exact=False):
        self.value = value
        self.op = operand
        self.exact = "!" if exact else ""

    def filter(self, card):
        raise NotImplementedError

    def dbfilter(self):
        pass

    def __str__(self):
        return "{exact}{key}{op}{value}".format(**self.__dict__)

class Name(Filter):
    def dbfilter(self):
        if self.exact:
            return Card.name == self.value
        else:
            return Card.name.contains(self.value)
        
        


class Negation:
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return "-{ex}".format(**self.__dict__)

    def dbfilter(self):
        return not_(self.ex.dbfilter) 

class Disjunction:
    def __init__(self, ex1, ex2):
        self.ex1 = ex1
        self.ex2 = ex2

    def filter(self, card):
        return self.ex1.filter(card) or self.ex2.filter(card)

    def dbfilter(self):
        return or_(self.ex1.dbfilter(), self.ex2.dbfilter())

    def __str__(self):
        return "({ex1} or {ex2})".format(**self.__dict__)

class Conjunction:
    def __init__(self, ex1, ex2):
        self.ex1 = ex1
        self.ex2 = ex2

    def filter(self, card):
        return self.ex1.filter(card) and self.ex2.filter(card)

    def dbfilter(self):
        return and_(self.ex1.dbfilter(), self.ex2.dbfilter())

    def __str__(self):
        return "{ex1} {ex2}".format(**self.__dict__)


list_of_filters = [
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

filterClasses = {l[0]: 
        type("tokenClass_%s" % l, (Filter,), {"key": l[0], "allkeys":l})
        for l in list_of_filters}

def findFilterClass(s):
    for l in list_of_filters:
        c = l[0]
        for j in l:
            if s == j:
                return filterClasses[c]

