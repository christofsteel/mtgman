from .model import Collection, CollectionCard, BaseCard, Printing, Edition
from .imports.edition import get_edition
from .imports.basecard import get_base_card
from .imports.printing import get_printing
import sys
import csv
from sqlalchemy.orm.exc import NoResultFound

def add_collection(name, parentname, session):
    parent = None
    if parentname:
        try:
            parent = session.query(Collection).filter(Collection.name == parent).one()
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

def import_cards(name, filename,session):
    try:
        collection = session.query(Collection).filter(Collection.name == name).one()
    except NoResultFound:
        print(f"could not find collection {name}")
        sys.exit(1)
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["count"] = int(row["count"])
            row["foil"] = True if "foil" in row and row["foil"].lower == "true" else False
            #try:
            #    edition = session.query(Edition).filter(Edition.code == row["edition"]).one()
            #except NoResultFound:
            #    edition = get_edition(row["edition"], session)
            #try:
            #    basecard = session.query(BaseCard)\
            #            .filter(BaseCard.edition == edition)\
            #            .filter(BaseCard.collector_number_str == row["cn"]).one()
            #except NoResultFound:
            #    basecard = get_base_card(edition, row["cn"], session)

            printing = get_printing(row["edition"], row["cn"], row["lang"], session)
            try:
                collection_card = session.query(CollectionCard)\
                        .filter(CollectionCard.collection == collection)\
                        .filter(CollectionCard.printing == printing)\
                        .filter(CollectionCard.foil == row["foil"])\
                        .filter(CollectionCard.condition == row["condition"]).one()

                collection_card.count += row["count"]
            except:
                collection_card = CollectionCard(collection = collection, printing = printing\
                        , foil = row["foil"], condition = row["condition"], count = row["count"])
                session.add(collection_card)
                session.commit()
