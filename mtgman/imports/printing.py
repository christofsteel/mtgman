from . import create_dict
from .scryfall import get_scryfall_printing
from .faces import get_card_face_from_sf, makeCardBaseFace, makeCardFacePrinting
from .basecard import get_base_card, get_base_card_from_sf, get_db_base_card_from_sf
from .edition import get_edition
from ..model import Printing, BaseCard, Edition

printing_rel_cache = {}

def printing_bulk_add(session):
    session.bulk_save_objects(printing_rel_cache.values(), return_defaults=True)
    session.commit()

def printing_prepare_bulk_add(element, session):
    base_card = get_db_base_card_from_sf(element, session)
    if get_db_printing(base_card, element["lang"], session) is None:
        printing_rel_cache[(base_card.id, element["lang"])] = \
                create_printing(element, base_card)

def get_db_printing(base_card, lang, session):
    return session.query(Printing).filter(Printing.base_card == base_card).filter(Printing.lang == lang).first()

def get_db_printing_from_sf(element, session):
    base_card = get_db_base_card_from_sf(element, session)
    if base_card is not None:
        return get_db_printing(base_card, element["lang"], session)
    return None

def get_printing(code, cn, lang, session):
    basecard = session.query(BaseCard).filter(BaseCard.edition_code == code).filter(BaseCard.collector_number_str == cn).first()
    if basecard is not None:
        printing = session.query(Printing)\
                .filter(Printing.base_card == basecard)\
                .filter(Printing.lang == lang).first()

        if printing is not None:
            return printing

    e = get_scryfall_printing(code, cn, lang) 
    printing = add_printing(e, session)
    
    session.commit()
    return printing

def create_printing(element, base_card):

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
    if type(base_card) is int:
        custom = {"base_card_id": base_card}
    else:
        custom = {"base_card": base_card}

    dict_all = create_dict(element, fields=fields, objects=objects, 
            renames_uuid=renames_uuid, custom=custom)

    printing = Printing(**dict_all)

    return printing #, gotten + list_all) 


def add_printing(e, session):
    base_card = get_base_card_from_sf(e, session)

    printing = create_printing(e, base_card)
    session.add(printing)
    fill_card_faces(e, session, printing=printing)
    return printing

def fill_card_faces(e, session, printing=None):
    if "card_faces" in e.keys():
        printing = get_db_printing_from_sf(e, session) if printing is None else printing
        for face in e["card_faces"]:
            card_face = get_card_face_from_sf(face, e, session)
            card_base_face = makeCardBaseFace(face, card_face, printing.base_card, session)
            makeCardFacePrinting(face, card_base_face, printing, session)
            session.commit()
