from datetime import datetime
from uuid import UUID

from sqlalchemy.orm.exc import NoResultFound

from .scryfall import get_scryfall_edition
from ..model import Edition, Block

def get_edition(code, session):
    try:
        return session.query(Edition).filter(Edition.code == code).one()
    except NoResultFound:
        sj = get_scryfall_edition(code) 
        edition = add_edition(sj, session)
        session.commit()
        return edition

def create_edition(edition, parent, block):
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
                       , parent = parent
                       , block = block
                       )
        return db_edition

def add_edition(element, session):
    block = None
    parent = None
    if element.get("block_code") is not None:
        block = session.query(Block).get(element.get("block_code"))
        if block is None:
            block = Block(code = element.get("block_code"), name = element.get("block"))
    if element.get("parent_set_code") is not None:
        parent = get_edition(element.get("parent_set_code"), session)
    edition = create_edition(element, parent, block)
    session.add(edition)
    return edition
