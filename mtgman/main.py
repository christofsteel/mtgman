from argparse import ArgumentParser
import datetime
import scrython
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .imports import import_sets, import_cards
from .dbactions import dbquery
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
    dbgroup.add_argument("--add", "-a", metavar="QUERY")
    dbgroup.add_argument("--query", "-q", metavar="QUERY")

    colparser = commands.add_parser("collection")
    # --add
    # --import file.cvs
    # --export query 

    args = parser.parse_args()    
    if args.command == "database" or args.command == "db":
        if args.add:
            import_cards(args.add, session)
        if args.query:
            dbquery(args.query, session)





    #import_sets(session)
    #import_cards(session)
    





if __name__ == "__main__":
    main()
