from .model import Collection, CollectionCard, BaseCard, Printing, Edition
from .imports.edition import get_edition
from .imports.basecard import get_base_card
from .imports.printing import get_printing
import sys
import csv
from sqlalchemy.orm.exc import NoResultFound
from .parser import parser

def make_query():
    pass

def show_collection(name, query, forma, session):
    db_query = session.query(CollectionCard).filter(Collection.name == name)
    db_query = make_query(db_query, query)
    breakpoint()

def add_collection(name, parentname, session):
    parent = None
    if parentname:
        try:
            parent = session.query(Collection).filter(Collection.name == parentname).one()
        except NoResultFound:
            print(f"Could not find parent {parent}")
            sys.exit(1)

    try:
        collection = Collection(name = name, parent = parent)
        session.add(collection)
        session.commit()
    except:
        print(f"Collection {name} already exists")
        sys.exit(1)

def list_collections(session):
    for collection in session.query(Collection).all():
        parentstr = f"{collection.parent.name}/" if collection.parent is not None else "" 
        print(f"{parentstr}{collection.name}")

def parse_count(count_string, foil, lang, condition):
    splitted = count_string.split("_")
    splitted = splitted[1:]
    while len(splitted) > 0:
        if splitted[0] == "foil":
            foil = splitted[0]
        elif splitted[0] == "nonfoil":
            foil = splitted[0]
        elif splitted[0] in ["m", "nm", "ex", "gd", "lp", "pl", "poor"]:
            condition = splitted[0]
        else:
            lang = splitted[0]
        splitted = splitted[1:]
    return foil, lang, condition

def parse_row(row, edition, foil, lang, condition):
    count_keys = [k for k in row.keys() if k.startswith("count")]
    for c in count_keys:
        try:
            count = int(row[c])
        except ValueError:
            continue
        
        foil, lang, condition = parse_count(c, foil, lang, condition)
        if lang:
            row["lang"]=lang
        if edition:
            row["edition"]=edition
        if foil:
            row["foil"]=foil
        if condition:
            row["condition"]=condition
        row["foil"] = True if "foil" in row and row["foil"].lower == "true" else False

        yield count, row["edition"], row["foil"], row["lang"], row["condition"]

def import_cards(name, filename, edition, foil, lang,condition,session):
    try:
        collection = session.query(Collection).filter(Collection.name == name).one()
    except NoResultFound:
        print(f"could not find collection {name}")
        sys.exit(1)
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for inputrow in parse_row(row, edition, foil, lang, condition):
                printing = get_printing(inputrow[1], row["cn"], inputrow[3], session)
                try:
                    collection_card = session.query(CollectionCard)\
                            .filter(CollectionCard.collection == collection)\
                            .filter(CollectionCard.printing == printing)\
                            .filter(CollectionCard.foil == inputrow[2])\
                            .filter(CollectionCard.condition == inputrow[4]).one()

                    collection_card.count += inputrow[0]
                except:
                    print("New card")
                    collection_card = CollectionCard(collection = collection, printing = printing\
                            , foil = inputrow[2], condition = inputrow[4], count = inputrow[0])
                    session.add(collection_card)
                    session.commit()
