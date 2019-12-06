from datetime import datetime

import scrython

from . import create_dict
from .edition import get_edition
from .card import create_card
from ..model import BaseCard

def get_base_card(code, cn, session):
    base_card = session.query(BaseCard).filter(BaseCard.collector_number_str == cn)\
            .filter(BaseCard.edition_code == code).first()

    if base_card is not None:
        return base_card

    sj = scrython.cards.collector.Collector(code=code,collector_number=cn).scryfallJson
    basecard = add_base_card(sj,session)
    session.commit()
    return basecard

def create_base_card(element, edition):
    card = create_card(element)

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
    custom = {"edition": edition, "card": card}
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
    base_card = create_base_card(e, edition) 
    session.add(base_card)
    return base_card
