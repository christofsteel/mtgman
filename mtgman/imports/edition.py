from datetime import datetime
from uuid import UUID

import scrython
from sqlalchemy.orm.exc import NoResultFound

from ..model import Edition, Block

def get_edition(code, session):
    try:
        return session.query(Edition).filter(Edition.code == code).one()
    except NoResultFound:
        sj = scrython.foundation.FoundationObject(f"sets/{code}?").scryfallJson
        edition = create_edition(sj, session)
        session.commit()
        return edition

def create_edition(edition, session):
        db_edition = Edition( scryfall_id = UUID(edition.get("id"))
                       , code = edition.get("code")
                       , mtgo_code = edition.get("mtgo_code")
                       , tcgplayer_id = edition.get("tcgplayer_id")
                       , name = edition.get("name")
                       , set_type = edition.get("set_type")
                       , released_at = datetime.strptime(edition.get("released_at"), "%Y-%m-%d")
                       , card_count = edition.get("card_count")
                       , digital = edition.get("digital")
                       , foil_only = edition.get("foil_only")
                       , scryfall_uri = edition.get("scryfall_uri")
                       , uri = edition.get("uri")
                       , icon_svg_uri = edition.get("icon_svg_uri")
                       , search_uri = edition.get("search_uri")
                       )
        if edition.get("block_code") is not None:
            block = session.query(Block).get(edition.get("block_code"))
            if block is None:
                block = Block(code = edition.get("block_code"), name = edition.get("block"))
                session.add(block)
            block.editions.append(db_edition)
        if edition.get("parent_set_code") is not None:
            parent = get_edition(edition.get("parent_set_code"), session)
            db_edition.parent_edition = parent
        session.add(db_edition)
        return db_edition
