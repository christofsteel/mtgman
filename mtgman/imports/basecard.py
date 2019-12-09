from datetime import datetime

from . import create_dict
from .scryfall import get_scryfall_base_card
from .edition import get_edition
from .card import get_card, get_card_from_sf
from ..model import BaseCard

base_card_rel_cache = {}

def base_card_bulk_add(session):
    session.bulk_save_objects(base_card_rel_cache.values(), return_defaults=True)
    session.commit()

def base_card_prepare_bulk_add(element, session):
    if (element["collector_number"], element["set"]) in base_card_rel_cache:
        return
    card = get_card(element["name"], session)
    if get_db_base_card_from_sf(element, session) is None:
        base_card_rel_cache[(element["collector_number"], element["set"])] = \
                create_base_card(element, card, element["set"])

def get_db_base_card(code, cn, session):
    return  session.query(BaseCard).filter(BaseCard.collector_number_str == cn)\
            .filter(BaseCard.edition_code == code).first()

def get_db_base_card_from_sf(e, session):
    return get_db_base_card(e["set"], e["collector_number"], session)

def get_base_card_from_sf(e, session):
    base_card = get_db_base_card_from_sf(e, session)
    if base_card is not None:
        return base_card
    base_card = add_base_card(e, session)
    session.commit()
    return base_card

def get_base_card(code, cn, session):
    base_card = get_db_base_card(code, cn, session)

    if base_card is not None:
        return base_card

    sj = get_scryfall_base_card(code, cn) 
    basecard = add_base_card(sj,session)
    session.commit()
    return basecard

def create_base_card(element, card, edition_code):

    fields = [ "highres_image", "games", "oversized", "promo", "reprint"
             , "variation", "digital", "rarity"
             , "card_back_id", "artist", "illustration_id", "border_color"
             , "frame", "full_art", "textless", "booster", "story_spotlight"
             , "flavor_text", "tcgplayer_id", "watermark", "arena_id"
             , "mtgo_id", "mtgo_foil_id"]
    fields_int = ["collector_number"]
    fields_date = ["released_at"]
    fields_uuid = ["variation_of"]
    lists = [ "multiverse_ids", "promo_types", "frame_effects"]
    lists_uuid = ["artist_ids"]
    objects = { 
            "preview": { 
                "previewed_at": ("previewed_at", lambda string:datetime.strptime(string, "%Y-%m-%d"))
                , "source": ("preview_source", lambda x:x)
                , "source_uri" : ("preview_source_uri", lambda x:x) },
            "prices": { 
                    "usd": ("price_usd", lambda x:float(x) if x is not None else x)
                    , "usd_foil": ("price_usd_foil", lambda x:float(x) if x is not None else x)
                    , "tix": ("price_tix", lambda x:float(x) if x is not None else x)
                    , "eur" : ("price_eur", lambda x:float(x) if x is not None else x) } 
            }
    renames = { "foil" : "has_foil", "nonfoil" : "has_nonfoil", "collector_number": "collector_number_str"}
    if type(card) is int:
        custom = {"edition_code": edition_code, "card_id": card}
    else:
        custom = {"edition_code": edition_code, "card": card}

    ignore = ["purchase_uris"]
    
    
    dict_all = create_dict(element, fields=fields, fields_date=fields_date,
            fields_uuid=fields_uuid, fields_int=fields_int, lists=lists, lists_uuid=lists_uuid, objects=objects,
            renames=renames, custom=custom, ignore=ignore)

    base_card = BaseCard(**dict_all)
    
    #if base_card is None:
    #    session.add(base_card)
    #    session.commit()
    #else: # update prices
    #    if e.get("prices").get("usd") is not None:
    #        base_card.price_usd = float(e.get("prices").get("usd"))
    #    if e.get("prices").get("usd_foil") is not None:
    #        base_card.price_usd_foil = float(e.get("prices").get("usd_foil"))
    #    if e.get("prices").get("eur") is not None:
    #        base_card.price_eur = float(e.get("prices").get("eur"))
    #    if e.get("prices").get("tix") is not None:
    #        base_card.price_tix = float(e.get("prices").get("tix"))
    #    session.add(base_card)
    return base_card#, gotten + list_all) 

def add_base_card(e, session):
    edition = get_edition(e.get("set"), session)
    card = get_card_from_sf(e, session)

    base_card = create_base_card(e, card, edition.code) 
    session.add(base_card)
    return base_card
