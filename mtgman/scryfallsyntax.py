import ply

class Token:    
    key = None
    allkeys = []

    def __init__(self, value, quoted=False, negated=False, operand=":"):
        self.value = value
        self.neg = "-" if negated else ""
        self.op = operand
        self.quotes = "\"" if quoted else ""

    def filter(self, cards):
        raise NotImplementedError

    def __str__(self):
        return "{neg}{key}{op}{q}{value}{q}".format(neg=self.neg, key=self.key, q=self.quotes, value=self.value, op=self.op)

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

def parse(q):
    splits = shlex.split(q)
    for split in splits:
        neg = split.startswith("-")
        if neg:
            split = split[1:]
        
