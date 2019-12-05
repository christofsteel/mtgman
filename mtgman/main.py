from argparse import ArgumentParser
import datetime
import scrython
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .imports import import_sets, import_cards
from .dbactions import dbquery
from .collections import add_collection, list_collections, import_cards
from .model import Base
import json
import os


def main():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    
    parser = ArgumentParser()
    commands = parser.add_subparsers(title="commands", dest="command")
    
    dbparser = commands.add_parser("database", aliases=["db"])
    dbgroup = dbparser.add_mutually_exclusive_group(required=True)
    dbgroup.add_argument("--get-editions", "-e", action="store_true")
    dbgroup.add_argument("--add", "-a", metavar="QUERY")
    dbgroup.add_argument("--query", "-q", metavar="QUERY")

    colparser = commands.add_parser("collection", aliases=["col"])
    colcommands = colparser.add_subparsers(dest="colcommand")
    newcol = colcommands.add_parser("new", aliases=["n"])
    newcol.add_argument("name")
    newcol.add_argument("--parent", "-p")
    editcol = colcommands.add_parser("edit", aliases=["e"])
    editcol.add_argument("name")
    editcol.add_argument("--query", '-q')    
    listcol = colcommands.add_parser("list", aliases=["l"])
    importcol = colcommands.add_parser("import", aliases=["i"])
    importcol.add_argument("name")
    importcol.add_argument("file")
    importcol.add_argument("--auto-add", '-a', action="store_true")
    importcol.add_argument("--edition", '-e')
    importcol.add_argument("--language", '-l')
    importcol.add_argument("--foil", '-f', action="store_true")

    # --add
    # --import file.cvs
    # --export query 

    args = parser.parse_args()    
    if args.command == "database" or args.command == "db":
        if args.get_editions:
            import_sets(session)
        elif args.add:
            import_cards(args.add, session)
        elif args.query:
            dbquery(args.query, session)
    elif args.command == "collection" or args.command == 'col':
        if args.colcommand == "new" or args.colcommand == "n":
            add_collection(args.name, args.parent, session)
        elif args.colcommand == "list" or args.colcommand == "l":
            list_collections(session)
        elif args.colcommand == "edit" or args.colcommand == "e":
            pass
        elif args.colcommand == "import" or args.colcommand == "i":
            import_cards(name = args.name, filename=args.file, session=session)





    #import_sets(session)
    #import_cards(session)
    





if __name__ == "__main__":
    main()
