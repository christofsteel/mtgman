from argparse import ArgumentParser
import datetime
import scrython
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .model import Card, BaseCard, Printing, Edition, Base, Block, part_of
from .dbactions import get_scryfall_cards, get_scryfall_sets, find_edition, find_by_scryfall_id
from uuid import UUID
import json

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

def addCard(e, session):
    fields = ['oracle_id', "prints_search_uri" , "rulings_uri", "cmc", \
              "reserved", "type_line", "name", "layout", "mana_cost", "oracle_text", \
              "edhrec_rank", "life_modifier", "hand_modifier"]
    fields_int = ['loyalty', "power", "toughness"]
    lists = ["colors", "color_identity", "color_indicator"]#, "legalities"]
    renames = { "power": "power_str"
              , "toughness": "toughness_str"
              , "loyalty": "loyalty_str"
              }
    custom = {}
    ignore = ["legalities", "all_parts"]

    dict_fields = {f:e.get(f) for f in fields}
    dict_fields_int = {f:(int(e.get(f)) if e.get(f) is not None and str(e.get(f)).isdigit() else None) for f in fields_int}
    dict_lists = {f:(e.get(f) if e.get(f) is not None else []) for f in lists}
    dict_renames = {v:e.get(k) for k,v in renames.items()}
    
    card = session.query(Card).filter(Card.oracle_id == e.get("oracle_id")).first()
    if card is None:
        card = Card(**dict_fields, **dict_lists, **dict_renames, **dict_fields_int, **custom)
    return (card, fields + lists + list(renames.keys()) + fields_int + ignore)

def addBaseCard(e, card, session):
    edition = session.query(Edition).filter(Edition.code == e.get("set")).one()
    fields = [ "highres_image"
             , "games"                       
             , "oversized"
             , "promo"
             , "reprint"
             , "variation"
             , "collector_number"
             , "digital"
             , "rarity"
             , "card_back_id"
             , "artist"
             , "illustration_id"
             , "border_color"
             , "frame"
             , "full_art"
             , "textless"
             , "booster"
             , "story_spotlight"
             , "flavor_text"
             , "tcgplayer_id"
             , "watermark"
             , "arena_id"
             , "mtgo_id"             
             , "mtgo_foil_id"             
             ]
    fields_int = []
    fields_date = ["released_at"]
    fields_uuid = ["variation_of"]
    lists = [ "multiverse_ids"
            , "promo_types"
            , "frame_effects"
            ]
    lists_uuid = ["artist_ids"]
    objects = { "preview": { "previewed_at": ("previewed_at", lambda string:datetime.datetime.strptime(string, "%Y-%m-%d"))
        , "source": ("preview_source", lambda x:x)
        , "source_uri" : ("preview_source_uri", lambda x:x)
        }
        }
    renames = { "foil" : "has_foil"
            , "nonfoil" : "has_nonfoil"
            }
    custom = {"edition": edition, "card": card}
    ignore = []

    dict_fields = {f:e.get(f) for f in fields}
    dict_fields_int = {f:(int(e.get(f)) if e.get(f) is not None and str(e.get(f)).isdigit() else None) for f in fields_int}
    dict_fields_date = {f:(datetime.datetime.strptime(e.get(f), "%Y-%m-%d") if e.get(f) is not None else None) for f in fields_date}
    dict_fields_uuid = {f:(UUID(e.get(f)) if e.get(f) is not None else None) for f in fields_uuid}
    dict_lists = {f:(e.get(f) if e.get(f) is not None else []) for f in lists}
    dict_lists_uuid = {f:[UUID(u) for u in e.get(f)] if e.get(f) is not None else [] for f in lists_uuid}
    dict_objects = {vv[0]:vv[1](e.get(f).get(k)) for f,v in objects.items() for k,vv in v.items() if e.get(f) is not None}
    dict_renames = {v:e.get(k) for k,v in renames.items()}
    
    base_card = session.query(BaseCard).filter(BaseCard.collector_number_str == e.get("collector_number"))\
            .filter(BaseCard.edition_code == e.get("set")).first()
    if base_card is None:
        base_card = BaseCard(**dict_fields
                            , **dict_fields_int
                            , **dict_fields_date
                            , **dict_fields_uuid
                            , **dict_lists
                            , **dict_lists_uuid
                            , **dict_objects
                            , **dict_renames
                            , **custom)
    return (base_card, fields + fields_int + fields_date + fields_uuid + lists + lists_uuid + list(objects.keys()) + list(renames.keys()) + ignore)


def addPrinting(e, base_card, session):
    fields = [ "lang"
             , "scryfall_uri"
             , "uri"
             , "printed_name"
             , "printed_text"
             , "printed_type_line"
             ]
    fields_int = []
    fields_date = []
    fields_uuid = []
    lists = [ 
            ]
    lists_uuid = []
    objects = { "image_uris": {
        "png": ("image_uri_png", lambda x: x)
        , "border_crop": ("image_uri_border_crop", lambda x: x)
        , "art_crop": ("image_uri_art_crop", lambda x: x)
        , "large": ("image_uri_large", lambda x: x)
        , "normal": ("image_uri_normal", lambda x: x)
        , "small": ("image_uri_small", lambda x: x)
        }
        }
    renames = { 
            }
    renames_uuid = {"id": "scryfall_id"}
    custom = {"base_card": base_card}
    ignore = []

    dict_fields = {f:e.get(f) for f in fields}
    dict_fields_int = {f:(int(e.get(f)) if e.get(f) is not None and str(e.get(f)).isdigit() else None) for f in fields_int}
    dict_fields_uuid = {f:(UUID(e.get(f)) if e.get(f) is not None else None) for f in fields_uuid}
    dict_fields_date = {f:(datetime.datetime.strptime(e.get(f), "%Y-%m-%d") if e.get(f) is not None else None) for f in fields_date}
    dict_lists = {f:(e.get(f) if e.get(f) is not None else []) for f in lists}
    dict_lists_uuid = {f:[UUID(u) for u in e.get(f)] if e.get(f) is not None else [] for f in lists_uuid}
    dict_objects = {vv[0]:vv[1](e.get(f).get(k)) for f,v in objects.items() for k,vv in v.items() if e.get(f) is not None}
    dict_renames = {v:e.get(k) for k,v in renames.items()}
    dict_renames_uuid = {v:(UUID(e.get(k)) if e.get(k) is not None else None) for k, v in renames_uuid.items()}
    
    printing = session.query(Printing).filter(Printing.scryfall_id==UUID(e.get("id"))).first()
    if printing is None:
        printing = Printing(**dict_fields
                            , **dict_fields_int
                            , **dict_fields_date
                            , **dict_fields_uuid
                            , **dict_lists
                            , **dict_lists_uuid
                            , **dict_objects
                            , **dict_renames
                            , **dict_renames_uuid
                            , **custom)
    return (printing, fields \
            + fields_int \
            + fields_date \
            + fields_uuid \
            + lists \
            + lists_uuid \
            + list(objects.keys()) \
            + list(renames.keys()) \
            + list(renames_uuid.keys()) \
            + ignore)

    

def main():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    editions = get_scryfall_sets()

    for idx, edition in enumerate(editions):
        print(f"({idx + 1}/{len(editions)}) {edition['name']}")
        addEdition(edition, editions, session)
    session.commit()

    #cards_online = get_scryfall_cards()
    #with open("cards.json", "w") as f:
    #    json.dump(cards_online, f)

    with open("cards.json", "r") as f:
        cards = json.load(f)

    for idx, e in enumerate(cards):
        got = ["object", "card_faces", "set", "set_name", "set_type", "set_uri", "set_search_uri", "scryfall_set_uri", "related_uris"]
        #def get(string):
        #    g = e.get(string)
        #    got.append(string)
        #    return g

        #def lget(string):
        #    g = e.get(string)
        #    got.append(string)
        #    return g if g is not None else []

        #def iget(string):
        #    g = e.get(string)
        #    got.append(string)
        #    return int(g) if g is not None and g.isdigit() else None

        #try:
        #    card = session.query(Card).filter(Card.oracle_id == e.get('oracle_id')).one()
        #    got += ['oracle_id', 'layout', 'cmc', 'power', 'colors', 'legalities', 'rulings_uri']
        #    got += ['name', 'type_line', 'color_indicator', 'color_identity', 'prints_search_uri']
        #    got += ['mana_cost', 'reserved', 'toughness', 'oracle_text', 'edhrec_rank', 'loyalty']
        #    got += ['life_modifier', 'hand_modifier']
        #except:
        #    card = Card( oracle_id = get('oracle_id')
        #               , prints_search_uri = get("prints_search_uri") 
        #               , rulings_uri = get("rulings_uri")
        #               , cmc = get("cmc")
        #               , reserved = get("reserved")
        #               , type_line = get("type_line")
        #               , name = get("name")
        #               , layout = get("layout")
        #               , mana_cost = get("mana_cost")
        #               , power_str = get("power")
        #               , power = iget("power")
        #               , toughness_str = get("toughness")
        #               , toughness = iget("toughness")
        #               , colors = lget("colors")
        #               , color_identity = lget("color_identity")
        #               , color_indicator = lget("color_indicator")
        #               , legalities = lget("legalities")
        #               , oracle_text = get("oracle_text")
        #               , edhrec_rank = get("edhrec_rank")
        #               , loyalty = iget('loyalty')
        #               , loyalty_str = get("loyalty")
        #               , life_modifier = get("life_modifier")
        #               , hand_modifier = get("hand_modifier")
        #               )            
        #    session.execute(part_of.insert(), [{"card_id1": card.id, "card_id2": card2id} for card2id in lget("all_parts")])
        #    session.add(card)
        card, got_card = addCard(e, session)
        got += got_card
        #try:
        #    base_card = session.query(BaseCard).join(Edition)\
        #            .filter(Edition.code == e['set'])\
        #            .filter(BaseCard.collector_number_str == e["collector_number"]).one()
        #    got += ['tcgplayer_id']
        #    got += ['frame_effects', "watermark"]
        #except NoResultFound:
        #    edition = session.query(Edition).filter(Edition.code == e.get("set")).one()
        #    base_card = BaseCard( card = card
        #                        , edition = edition                                
        #                        , multiverse_ids = lget("multiverse_ids")
        #                        , released_at = datetime.datetime.strptime(get("released_at"), "%Y-%m-%d")
        #                        , highres_image = get("highres_image")
        #                        , has_foil = get("foil")
        #                        , has_nonfoil = get("nonfoil")
        #                        , games = get("games")                       
        #                        , oversized = get("oversized")
        #                        , promo = get("promo")
        #                        , promo_types = lget("promo_types")
        #                        , reprint = get("reprint")
        #                        , variation = get("variation")
        #                        , collector_number = get("collector_number")
        #                        , digital = get("digital")
        #                        , rarity = get("rarity")
        #                        , card_back_id = get("card_back_id")
        #                        , artist = get("artist")
        #                        , artist_ids = [UUID(u) for u in get("artist_ids")] if get("artist_ids") is not None else []
        #                        , illustration_id = get("illustration_id")
        #                        , border_color = get("border_color")
        #                        , frame = get("frame")
        #                        , full_art = get("full_art")
        #                        , textless = get("textless")
        #                        , booster = get("booster")
        #                        , story_spotlight = get("story_spotlight")
        #                        , flavor_text = get("flavor_text")
        #                        , tcgplayer_id = get("tcgplayer_id")
        #                        , frame_effects = lget("frame_effects")
        #                        , watermark = get("watermark")
        #                        , previewed_at = datetime.datetime.strptime(get("preview").get("previewed_at"), "%Y-%m-%d") if get("preview") is not None else None
        #                        , preview_source_uri = get("preview").get("source_uri") if get("preview") is not None else None
        #                        , preview_source = get("preview").get("source") if get("preview") is not None else None
        #                        , arena_id = get("arena_id")

        #                        )
        #    session.add(base_card)
        base_card, gotten = addBaseCard(e, card, session)
        got += gotten
        #try:
        #    printing = session.query(Printing).filter(Printing.scryfall_id == UUID(e.get("id"))).one()
        #    print(f"({idx + 1}/{len(cards)}) (X) {printing.base_card.card.name}, {printing.base_card.edition.code}, {printing.base_card.collector_number}, {printing.lang}")        
        #    got += ['id', 'lang', 'uri', 'scryfall_uri', 'image_uris']
        #    got += ['printed_name', 'printed_text', 'printed_type_line']
        #except NoResultFound:
        #    printing = Printing( base_card=base_card
        #                       , scryfall_id = UUID(get("id"))
        #                       , lang = get("lang")
        #                       , scryfall_uri = get("scryfall_uri")
        #                       , uri = get("uri")
        #                       , image_uri_png = get("image_uris").get("png") if get("image_uris") is not None else None
        #                       , image_uri_border_crop = get("image_uris").get("border_crop") if get("image_uris") is not None else None
        #                       , image_uri_art_crop = get("image_uris").get("art_crop") if get("image_uris") is not None else None
        #                       , image_uri_large = get("image_uris").get("large") if get("image_uris") is not None else None
        #                       , image_uri_normal = get("image_uris").get("normal") if get("image_uris") is not None else None
        #                       , image_uri_small = get("image_uris").get("small") if get("image_uris") is not None else None
        #                       , printed_name = get("printed_name")
        #                       , printed_text = get("printed_text")
        #                       , printed_type_line = get("printed_type_line")
        #                       )
        #    session.add(printing)
        printing, gotten = addPrinting(e, base_card, session)        
        got += gotten
        session.add(printing)
        print(f"({idx + 1}/{len(cards)}) {printing.base_card.card.name}, {printing.base_card.edition.code}, {printing.base_card.collector_number}, {printing.lang}")        

        missing = [k for k in e.keys() if k not in got]
        if missing != []:
            print("missing fields: {}".format(missing))            
            print("got fields: {}".format(sorted(got)))            
            b = []
            c = []
            p = []
            for k in missing:
                if k in BaseCard.__dict__.keys():
                    b.append(k)
                    missing.remove(k)
                if k in Card.__dict__.keys():
                    c.append(k)
                    missing.remove(k)
                if k in Printing.__dict__.keys():
                    p.append(k)
                    missing.remove(k)
            print("Basecard")
            for k in b:
                print(f"                                , {k} = get(\"{k}\")")
            print(f"            got += {b}")
            print("Card")
            for k in c:
                print(f"                       , {k} = get(\"{k}\")")
            print(f"got += {c}")

            print("Printing")
            for k in p:
                print(f"                           , {k} = get(\"{k}\")")
            print(f"got += {p}")
                    
            for k in missing:
                print(f"{k} : {e[k]}")
            return
    session.commit()
        #print(json.dumps(e, indent=2, sort_keys = True))




if __name__ == "__main__":
    main()
