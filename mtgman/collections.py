from .model import Collection
import sys

def add_collection(name, parentname, session):
    parent = None
    if parentname:
        try:
            parent = session.query(Collection).filter(Collection.name == parent).one()
        except:
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
