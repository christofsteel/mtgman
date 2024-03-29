from sqlalchemy.orm.exc import NoResultFound

from . import create_dict
from .scryfall import get_scryfall_card
from ..model import Card, Legality

#def import_cards(query, session):
#    cards = get_scryfall_cards(query)
#
#    for e in tqdm(cards):
#        edition = get_edition(e["set"], session)
#        printing = createPrinting(e, edition) 
#        session.add(printing)
#        gotten_card_faces = fillCardFaces(e, printing, session)
#        session.add(printing)
#    session.commit()

card_rel_cache = {}

def card_bulk_add(session):
    session.bulk_save_objects(card_rel_cache.values(), return_defaults=True)
    session.commit()


def card_prepare_bulk_add(element, session):
    if element["name"] in card_rel_cache:
        return
    if get_db_card_from_sf(element, session) is None:
        card_rel_cache[element["name"]] = create_card(element)

def get_db_card(name, session):
    return session.query(Card).filter(Card.name == name).first()

def get_db_card_from_sf(e, session):
    return get_db_card(e["name"], session)

def get_card_from_sf(e, session):
    card = get_db_card_from_sf(e, session)
    if card is not None:
        return card
    card = add_card(e, session)
    session.commit()
    return card

def get_card(name, session):
    card = get_db_card(name, session)
    if card is not None:
        return card

    e = get_scryfall_card(name)
    card = add_card(e, session)
    session.commit()
    return card


def create_card(element):
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
            for fmt, status in element.get("legalities").items()]
            }
    ignore = ["legalities", "all_parts"]

    dict_all = create_dict(element, fields=fields, fields_int=fields_int
            ,lists=lists, renames=renames, custom=custom, ignore=ignore)

    return Card(**dict_all)


def add_card(e, session):
    card = create_card(e)
    session.add(card)
    return card
