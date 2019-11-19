#/usr/bin/env python

import argparse
import scrython

def format_pos_arg(key, value):
    if value.startswith(">") or \
            value.startswith("<") or \
            value.startswith("=") or \
            value.startswith("!="):
                return key + value
    else:
        return key + ":" + "\"" + value + "\""

def format_neg_arg(key, value):
    return "-" + format_pos_arg(key.lower(), value)

def format_args_to_query_string(args : argparse.Namespace, ignore=[]):
    q = []
    for key, value in vars(args).items():
        if value is not None and key not in ignore:
            for v in value:
                if key[0].isupper():
                    q.append(format_neg_arg(key, v))
                else:
                    q.append(format_pos_arg(key, v))
    return " ".join(q)



def main():
    parser = argparse.ArgumentParser()
    commands_parser = parser.add_subparsers(dest="command", help="commands")
    search_parser = commands_parser.add_parser("search", help = "search scryfall")
    search_parser.add_argument("--output", default="{name}", help="Output formatter")
    search_parser.add_argument("--extras", action="store_const", const=["extras"], dest="include", help="Include extra cards like vanguard, etc.")
    search_parser.add_argument("--has", action="append", help="General has expression")
    search_parser.add_argument("--is", action="append", help="General is expression")
    search_parser.add_argument("--color", "-c", action="append", help="Colors to match. May include comparison expressions")
    search_parser.add_argument("--Color", "-C", action="append", help="Colors to exclude. May include comparison expressions")
    search_parser.add_argument("--id", action="append", help="Colors IDs to match. May include comparison expressions")
    search_parser.add_argument("--Id", action="append", help="Colors IDs to exclude. May include comparison expressions")
    search_parser.add_argument("--type", "-t", action="append", help="Card type to match")
    search_parser.add_argument("--Type", "-T", action="append", help="Card type to exclude")
    search_parser.add_argument("--oracle", "-o", action="append", help="Oracle text to match. Use ~ for card name")
    search_parser.add_argument("--Oracle", "-O", action="append", help="Oracle text to exclude. Use ~ for card name")
    search_parser.add_argument("--fo", action="append", help="Full oracle text (including reminder) to match. Use ~ for card name")
    search_parser.add_argument("--Fo", action="append", help="Full oracle text (including reminder) to exclude. Use ~ for card name")
    search_parser.add_argument("--mana", "-m", action="append", help="Mana costs to match. May include comparison expressions")
    search_parser.add_argument("--Mana", "-M", action="append", help="Mana costs to exclude. May include comparison expressions")
    search_parser.add_argument("--pow", action="append", help="Power to find. May include comparison expressions")
    search_parser.add_argument("--Pow", action="append", help="Power to exclude. May include comparison expressions")
    search_parser.add_argument("--tou", action="append", help="Toughness to find. May include comparison expressions")
    search_parser.add_argument("--Tou", action="append", help="Toughness to exclude. May include comparison expressions")
    search_parser.add_argument("--pt", action="append", help="Total power and Toughness to find. May include comparison expressions")
    search_parser.add_argument("--Pt", action="append", help="Total power and Toughness to exclude. May include comparison expressions")
    search_parser.add_argument("--loy", action="append", help="Loyality to find. May include comparison expressions")
    search_parser.add_argument("--Loy", action="append", help="Loyality to exclude. May include comparison expressions")
    search_parser.add_argument("--rarity", "-r", action="append", help="Rarity to match. May include comparison expressions")
    search_parser.add_argument("--Rarity", "-R", action="append", help="Rarity to exclude. May include comparison expressions")
    search_parser.add_argument("--set", "-s", action="append", help="Matches the exact card in the given set")
    search_parser.add_argument("--Set", "-S", action="append", help="Excludes the card in the given set")
    search_parser.add_argument("--cn", action="append", help="Collectors number to match. May include comparison expressions")
    search_parser.add_argument("--Cn", action="append", help="Collectors number to exclude. May include comparison expressions")
    search_parser.add_argument("--block", "-b", action="append", help="Block to match")
    search_parser.add_argument("--Block", "-B", action="append", help="Block to exclude")
    search_parser.add_argument("--in", action="append", help="Matches cards that have a printing in a given set (May also include broader terms like \"core\")")
    search_parser.add_argument("--In", action="append", help="Excludes cards that have a printing in a given set (May also include broader terms like \"core\")")
    search_parser.add_argument("--st", action="append", help="Matches categories of products")
    search_parser.add_argument("--St", action="append", help="Excludes categories of products")
    search_parser.add_argument("--cube", action="append", help="Matches cards that are part of cube lists")
    search_parser.add_argument("--Cube", action="append", help="Excludes cards that are part of cube lists")
    search_parser.add_argument("--format", "-f", action="append", help="Format legality to match")
    search_parser.add_argument("--Format", "-F", action="append", help="Format legality to exclude")
    search_parser.add_argument("--banned", action="append", help="Format banning to match")
    search_parser.add_argument("--Banned", action="append", help="Format banning to exclude")
    search_parser.add_argument("--restricted", action="append", help="Format restrictions to match")
    search_parser.add_argument("--Restricted", action="append", help="Format restrictions to exclude")
    search_parser.add_argument("--usd", action="append", help="Matches price in USD. May include comparison expressions")
    search_parser.add_argument("--Usd", action="append", help="Excludes price in USD. May include comparison expressions")
    search_parser.add_argument("--eur", action="append", help="Matches price in EUR. May include comparison expressions")
    search_parser.add_argument("--Eur", action="append", help="Excludes price in EUR. May include comparison expressions")
    search_parser.add_argument("--tix", action="append", help="Matches price in TIX. May include comparison expressions")
    search_parser.add_argument("--Tix", action="append", help="Excludes price in TIX. May include comparison expressions")
    search_parser.add_argument("--artist", "-a", action="append", help="Artist to match")
    search_parser.add_argument("--Artist", "-A", action="append", help="Artist to exclude")
    search_parser.add_argument("--ft", action="append", help="Flavor text to match")
    search_parser.add_argument("--Ft", action="append", help="Flavor text to exclude")
    search_parser.add_argument("--wm", action="append", help="Water mark to match")
    search_parser.add_argument("--Wm", action="append", help="Water mark to exclude")
    search_parser.add_argument("--new", action="append", help="Specifies that something has to be new in a printing, eg. art, artist or flavor")
    search_parser.add_argument("--New", action="append", help="Specifies that something has to remain old in a printing, eg. art, artist or flavor")
    search_parser.add_argument("--illustrations", action="append", help="Amount of illustrations to match. May including comparison expressions")
    search_parser.add_argument("--Illustrations", action="append", help="Amount of illustrations to exclude. May including comparison expressions")
    # border
    # frame
    # game
    # year
    # date
    # prints
    # sets
    # paperprints
    # papersets
    # language
    # exact (!)
    # unique
    # prefer
    search_parser.add_argument("--query", "-q", help="add manual a query", default="")
    search_parser.add_argument("name", help="Matches part of the name", default="", nargs="?")
    

    args = parser.parse_args()
    if args.command == "search":
        q = format_args_to_query_string(args, ignore=["output", "query", "name", "command"]) + " " + args.query + " " + args.name
        cardlist = []
        
        page = 1
        try:
            res = scrython.cards.Search(q=q, page=page)
        except scrython.foundation.ScryfallError as e:
            print(e.obj)
            

        total_cards = res.total_cards()
        cardlist = res.data() 

        while res.has_more():
            page += 1
            res = scrython.cards.Search(q=q, page=page)
            cardlist += res.data() 

        for card in cardlist:
            print(args.output.format(**card))
        print(cardlist[0].keys())

        print("Total: %d" % total_cards)
        print("Query:\n\t%s" % q)

if __name__ == "__main__":
    main()
