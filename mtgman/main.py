from argparse import ArgumentParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Base

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
    #dbgroup.add_argument("--get-editions", "-e", action="store_true")
    #dbgroup.add_argument("--fetch", "-f", metavar="QUERY")
    dbgroup.add_argument("--update", "-u", action="store_true")
    dbgroup.add_argument("--query", "-q", metavar="QUERY")

    colparser = commands.add_parser("collection", aliases=["col"])
    colcommands = colparser.add_subparsers(dest="colcommand")
    newcol = colcommands.add_parser("new", aliases=["n"])
    newcol.add_argument("name")
    newcol.add_argument("--parent", "-p")
    exportcol = colcommands.add_parser("export", aliases=["e"])
    exportcol.add_argument("name")
    exportcol.add_argument("--query", '-q')
    exportcol.add_argument("--group", "-g")
    editcol = colcommands.add_parser("update", aliases=["u"])
    editcol.add_argument("name")
    editcol.add_argument("--query", '-q')    
    showcol = colcommands.add_parser("show", aliases=["s"])
    showcol.add_argument("name")
    showcol.add_argument("--query", '-q')
    showcol.add_argument("--format", "-f")
    listcol = colcommands.add_parser("list", aliases=["l"])
    importcol = colcommands.add_parser("import", aliases=["i"])
    importcol.add_argument("name")
    importcol.add_argument("file")
    importcol.add_argument("--auto-add", '-a', action="store_true")
    importcol.add_argument("--edition", '-e')
    importcol.add_argument("--language", '-l')
    importcol.add_argument("--condition", '-c')
    importcol.add_argument("--foil", '-f')

    args = parser.parse_args()    
    if args.command == "database" or args.command == "db":
        #if args.get_editions:
        #    import_sets(session)
        #if args.fetch:            
        #    from .imports.fetch import import_cards_from_query
        #    import_cards_from_query(args.fetch, session)
        if args.query:
            from .dbactions import dbquery
            dbquery(args.query, session)
        elif args.update:
            from .imports.fetch import import_cards_from_bulk
            import_cards_from_bulk(0, session)
    elif args.command == "collection" or args.command == 'col':
        from .collections import add_collection, list_collections, show_collection, import_cards
        if args.colcommand == "new" or args.colcommand == "n":
            add_collection(args.name, args.parent, session)
        elif args.colcommand == "show" or args.colcommand == "s":
            show_collection(args.name, args.query, args.format, session)
        elif args.colcommand == "list" or args.colcommand == "l":
            list_collections(session)
        elif args.colcommand == "update" or args.colcommand == "u":
            raise NotImplementedError
        elif args.colcommand == "import" or args.colcommand == "i":
            import_cards(args.name, args.file, args.edition, args.foil, args.language, args.condition, session)
        else:
            raise NotImplementedError

if __name__ == "__main__":
    main()
