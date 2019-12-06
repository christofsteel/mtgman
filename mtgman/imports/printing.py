import scrython

from . import create_dict
from .faces import fillCardFaces
from .basecard import get_base_card
from .edition import get_edition
from ..model import Printing, BaseCard, Edition

def get_printing(code, cn, lang, session):
    printing = session.query(Printing).join(BaseCard, aliased=True).join(Edition, aliased=True)\
            .filter(BaseCard.collector_number_str == cn)\
            .filter(Edition.code == code)\
            .filter(Printing.lang == lang).first()

    if printing is not None:
        return printing

    e = scrython.cards.collector.Collector(code=code,collector_number=cn, lang=lang).scryfallJson

    printing = add_printing(e, session)
    
    session.commit()
    return printing

def create_printing(element, base_card, edition):

    fields = [ "lang", "scryfall_uri", "uri", "printed_name", "printed_text"
            , "printed_type_line"]
    objects = { "image_uris": {
        "png": ("image_uri_png", lambda x: x)
        , "border_crop": ("image_uri_border_crop", lambda x: x)
        , "art_crop": ("image_uri_art_crop", lambda x: x)
        , "large": ("image_uri_large", lambda x: x)
        , "normal": ("image_uri_normal", lambda x: x)
        , "small": ("image_uri_small", lambda x: x)
        }
        }
    renames_uuid = {"id": "scryfall_id"}
    custom = {"base_card": base_card}

    dict_all = create_dict(element, fields=fields, objects=objects, 
            renames_uuid=renames_uuid, custom=custom)

    printing = Printing(**dict_all)

    return printing #, gotten + list_all) 


def add_printing(e, session):
    edition = get_edition(e.get("set"), session)
    base_card = get_base_card(e.get("set"), e.get("collector_number"), session)

    printing = create_printing(e, base_card, edition)
    fillCardFaces(e, printing, session)
    session.add(printing)
    return printing

