from argparse import ArgumentParser
import datetime
import scrython
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import *
from .dbactions import get_scryfall_cards, get_scryfall_sets
from uuid import UUID


def main():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    editions = get_scryfall_sets()
    parent_edition_rel = {}
    

    for idx, edition in enumerate(editions):
        print(f"({idx + 1}/{len(editions)}) {edition['name']}")

        db_edition = Edition( scryfall_id = UUID(edition.get("id"))
                       , code = edition.get("code")
                       , mtgo_code = edition.get("mtgo_code")
                       , tcgplayer_id = edition.get("tcgplayer_id")
                       , name = edition.get("name")
                       , set_type = edition.get("set_type")
                       , released_at = datetime.datetime.strptime(edition.get("released_at"), "%Y-%m-%d")
                       , card_count = edition.get("card_count")
                       , digital = edition.get("digital")
                       , foil_only = edition.get("foil_only")
                       , scryfall_uri = edition.get("scryfall_uri")
                       , uri = edition.get("uri")
                       , icon_svg_uri = edition.get("icon_svg_uri")
                       , search_uri = edition.get("search_uri")
                       )
        session.add(db_edition)
        if edition.get("block_code") is not None:
            try:
                block = session.query(Block).filter_by(code = edition.get("block_code")).one()
                block.editions.append(db_edition)
            except:
                block = Block(code = edition.get("block_code"), name = edition.get("block"))
                block.editions.append(db_edition)
                session.add(block)
        if edition.get("parent_set_code") is not None:
            if db_edition.id is None:
                session.commit()
            parent_edition_rel[db_edition.id] = edition.get("parent_set_code")


    for ed, parent in parent_edition_rel.items():
        child_edition = session.query(Edition).get(ed)
        parent_edition = session.query(Edition).filter_by(code = parent).one()
        parent_edition.child_editions.append(child_edition)

    session.commit()
    
    cards = get_scryfall_cards()
    for card in cards:
        



if __name__ == "__main__":
    main()
