import os
import json
import datetime
from uuid import UUID

from tqdm import tqdm

from .model import Card, BaseCard, Printing, Edition, Base, Block, Parts, Legality, CardFace, CardFaceBase, CardFacePrinting
from .dbactions import get_scryfall_cards, get_scryfall_sets, find_edition, find_by_scryfall_id

def import_sets(session):
    editions = get_scryfall_sets()

    for edition in tqdm(editions):
        addEdition(edition, editions, session)
    session.commit()

def import_cards(query, session):
    cards = get_scryfall_cards(query)

    for e in tqdm(cards):
        printing, gotten = addPrinting(e, session)        
        gotten_card_faces = fillCardFaces(e, printing, session)
        session.add(printing)
    session.commit()


def addEdition(edition, json, session):
        ed = session.query(Edition).get(edition.get("code"))
        if ed is not None:
            return ed
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
        if edition.get("block_code") is not None:
            block = session.query(Block).get(edition.get("block_code"))
            if block is None:
                block = Block(code = edition.get("block_code"), name = edition.get("block"))
                session.add(block)
            block.editions.append(db_edition)
        if edition.get("parent_set_code") is not None:
            par_ed = session.query(Edition).get(edition.get("parent_set_code"))
            if par_ed is None:
                parent = find_edition(json, edition.get("parent_set_code"))
                par_ed = addEdition(parent, json,session)
                session.add(par_ed)
            db_edition.parent_edition = par_ed
        session.add(db_edition)
        return db_edition

def is_simpl_digit(i):
    i in "0123456789"

def create_dict( e
               , fields = [] 
               , fields_int = []
               , fields_date = []
               , fields_uuid = []
               , lists = []
               , lists_uuid = []
               , renames = {}
               , renames_uuid = {}
               , objects = {}
               , custom = {}
               , ignore = []):
    dict_fields = {f:e.get(f) for f in fields}
    dict_fields_int = {f:(int("".join(filter(is_simpl_digit,e.get(f)))) if "".join(filter(is_simpl_digit,e.get(f))).isdigit() else 0) for f in fields_int if e.get(f) is not None}
    dict_fields_date = {f:(datetime.datetime.strptime(e.get(f), "%Y-%m-%d") if e.get(f) is not None else None) for f in fields_date}
    dict_fields_uuid = {f:(UUID(e.get(f)) if e.get(f) is not None else None) for f in fields_uuid}
    dict_lists = {f:(e.get(f) if e.get(f) is not None else []) for f in lists}
    dict_lists_uuid = {f:[UUID(u) for u in e.get(f)] if e.get(f) is not None else [] for f in lists_uuid}
    dict_renames = {v:e.get(k) for k,v in renames.items()}
    dict_renames_uuid = {v:(UUID(e.get(k)) if e.get(k) is not None else None) for k, v in renames_uuid.items()}
    dict_objects = {vv[0]:vv[1](e.get(f).get(k)) for f,v in objects.items() for k,vv in v.items() if e.get(f) is not None}
    dict_all = { **dict_fields, **dict_fields_int, **dict_fields_date
               , **dict_fields_uuid, **dict_lists, **dict_lists_uuid
               , **dict_renames, **dict_renames_uuid, **dict_objects, **custom}
    list_all = fields + fields_int + fields_date + fields_uuid\
             + lists + lists_uuid + list(renames.keys()) + list(renames_uuid.keys())\
             + list(objects.keys()) + ignore
    return dict_all, list_all
             
def makeCardFacePrinting(e, card_base_face, printing, session):
    fields = ["printed_name", "printed_text", "printed_type_line"]
    objects = { "image_uris": {
        "png": ("image_uri_png", lambda x: x)
        , "border_crop": ("image_uri_border_crop", lambda x: x)
        , "art_crop": ("image_uri_art_crop", lambda x: x)
        , "large": ("image_uri_large", lambda x: x)
        , "normal": ("image_uri_normal", lambda x: x)
        , "small": ("image_uri_small", lambda x: x)
        }
        }
    custom = {"card_face_base": card_base_face, "card_printing": printing}

    dict_all, list_all = create_dict(e, fields=fields, objects=objects, custom=custom)
    card_face_printing = session.query(CardFacePrinting)\
        .filter(CardFacePrinting.card_face_base == card_base_face)\
        .filter(CardFacePrinting.card_printing == printing).first()

    if card_face_printing is None:
        card_face_printing = CardFacePrinting(**dict_all)
        session.add(card_face_printing)

    return list_all

def makeCardBaseFace(face, card_face, basecard, session):
    fields = ["artist", "flavor_text", "watermark"]
    fields_uuid = ["artist_id", "illustration_id"]
    custom = {"card_face" : card_face, "basecard": basecard}

    dict_all, list_all = create_dict(face, fields=fields, fields_uuid=fields_uuid, custom = custom)

    card_base_face = session.query(CardFaceBase)\
            .filter(CardFaceBase.card_face == card_face)\
            .filter(CardFaceBase.basecard == basecard).first()

    if card_base_face is None:
        card_base_face = CardFaceBase(**dict_all)
        session.add(card_base_face)

    return card_base_face, list_all

def makeCardFace(face, card, session):
    fields = ["name", "mana_cost", "type_line", "oracle_text"]
    fields_int = ["power", "toughness"]
    lists=["colors", "color_indicator"]
    fields_uuid = []
    renames = {"power": "power_str", "toughness": "toughness_str"}
    custom = {"card": card}
    dict_all, list_all = create_dict(face, fields=fields, lists=lists, fields_int=fields_int, fields_uuid=fields_uuid, renames=renames, custom=custom)

    card_face = session.query(CardFace).filter(CardFace.name == face["name"]).first()

    if card_face is None:
        card_face = CardFace(**dict_all)
        session.add(card_face)

    return card_face, list_all
    


def addCard(e, session, get_parts_stack = []): 
    fields = ['oracle_id', "prints_search_uri" , "rulings_uri", "cmc", \
              "reserved", "type_line", "name", "layout", "mana_cost", "oracle_text", \
              "edhrec_rank", "life_modifier", "hand_modifier"]
    fields_int = ['loyalty', "power", "toughness"]
    lists = ["colors", "color_identity", "color_indicator"]# "legalities"]
    renames = { "power": "power_str"
              , "toughness": "toughness_str"
              , "loyalty": "loyalty_str"
              }
    custom = {"legalities": \
            [Legality(fmt=fmt,status=status) \
            for fmt, status in e.get("legalities").items()]
            }
    ignore = ["legalities", "all_parts"]
    card = session.query(Card).filter(Card.oracle_id == e.get("oracle_id")).first()
    dict_all, list_all = create_dict(e, fields=fields, fields_int=fields_int
            ,lists=lists, renames=renames, custom=custom, ignore=ignore)

    if card is None:
        card = Card(**dict_all)
        session.add(card)
        # get related cards
        # these change to often and can lead to inconsitent states when updating
        #all_parts = []
        #if "all_parts" in e:
        #    for part in e.get("all_parts"):
        #        if part.get("id") not in get_parts_stack and part.get("id") != e.get("id"):
        #            e_part = find_by_scryfall_id(all_cards, part.get("id"))
        #            card_part, _ = addCard(e_part
        #                    , all_cards, session
        #                    , get_parts_stack=get_parts_stack + [e.get("id")])
        #            session.add(card_part)
        #            part_part = Parts(card1 = card, card2 = card_part, card_component = part.get("component"))
        #            all_parts.append(part_part)
        #print(f"New card {card.name}")
    return card, list_all 
    #builder = CardBuilder(e, session, all_cards)
    #card, lists = builder.create_object(), builder.get_list()
    #session.add(card)
    #session.commit()
    #return card, lists

def addBaseCard(e, session):
    card, gotten = addCard(e, session)

    edition = session.query(Edition).filter(Edition.code == e.get("set")).one()

    #builder = BaseCardBuilder(e, session) 
    #base_card = builder.create_object()
    #base_card.card = card
    #base_card.edition = edition

    #return (base_card, gotten + builder.get_list())
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
                "previewed_at": ("previewed_at", lambda string:datetime.datetime.strptime(string, "%Y-%m-%d"))
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
    
    
    dict_all, list_all = create_dict(e, fields=fields, fields_date=fields_date,
            fields_uuid=fields_uuid, fields_int=fields_int, lists=lists, lists_uuid=lists_uuid, objects=objects,
            renames=renames, custom=custom, ignore=ignore)
    
    base_card = session.query(BaseCard).filter(BaseCard.collector_number_str == e.get("collector_number"))\
            .filter(BaseCard.edition_code == e.get("set")).first()
    if base_card is None:
        base_card = BaseCard(**dict_all)
        session.add(base_card)
        session.commit()
    else: # update prices
        if e.get("prices").get("usd") is not None:
            base_card.price_usd = float(e.get("prices").get("usd"))
        if e.get("prices").get("usd_foil") is not None:
            base_card.price_usd_foil = float(e.get("prices").get("usd_foil"))
        if e.get("prices").get("eur") is not None:
            base_card.price_eur = float(e.get("prices").get("eur"))
        if e.get("prices").get("tix") is not None:
            base_card.price_tix = float(e.get("prices").get("tix"))
        session.add(base_card)
    return (base_card, gotten + list_all) 


def addPrinting(e, session):
    base_card, gotten = addBaseCard(e, session)

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

    dict_all, list_all = create_dict(e, fields=fields, objects=objects, 
            renames_uuid=renames_uuid, custom=custom)

    printing = session.query(Printing).filter(Printing.scryfall_id==UUID(e.get("id"))).first()
    if printing is None:
        printing = Printing(**dict_all)
    return (printing, gotten + list_all) 

def fillCardFaces(e, printing, session):
    gotten = []
    gotten2 = []
    gotten3 = []
    if "card_faces" in e.keys():
        for face in e["card_faces"]:
            card_face, gotten = makeCardFace(face, printing.base_card.card, session)
            card_base_face, gotten2 = makeCardBaseFace(face, card_face, printing.base_card, session)
            gotten3 = makeCardFacePrinting(face, card_base_face, printing, session)
            session.commit()

    return gotten + gotten2 + gotten3

