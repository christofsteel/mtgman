from argparse import ArgumentParser
import datetime
import scrython
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .model import Card, BaseCard, Printing, Edition, Base, Block
from .dbactions import get_scryfall_cards, get_scryfall_sets
from uuid import UUID
import json


def main():
    engine = create_engine("sqlite:///test.db")
    Session = sessionmaker()
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    #editions = get_scryfall_sets()
    #parent_edition_rel = {}
    

    #for idx, edition in enumerate(editions):
    #    print(f"({idx + 1}/{len(editions)}) {edition['name']}")

    #    db_edition = Edition( scryfall_id = UUID(edition.get("id"))
    #                   , code = edition.get("code")
    #                   , mtgo_code = edition.get("mtgo_code")
    #                   , tcgplayer_id = edition.get("tcgplayer_id")
    #                   , name = edition.get("name")
    #                   , set_type = edition.get("set_type")
    #                   , released_at = datetime.datetime.strptime(edition.get("released_at"), "%Y-%m-%d")
    #                   , card_count = edition.get("card_count")
    #                   , digital = edition.get("digital")
    #                   , foil_only = edition.get("foil_only")
    #                   , scryfall_uri = edition.get("scryfall_uri")
    #                   , uri = edition.get("uri")
    #                   , icon_svg_uri = edition.get("icon_svg_uri")
    #                   , search_uri = edition.get("search_uri")
    #                   )
    #    session.add(db_edition)
    #    if edition.get("block_code") is not None:
    #        try:
    #            block = session.query(Block).filter_by(code = edition.get("block_code")).one()
    #            block.editions.append(db_edition)
    #        except:
    #            block = Block(code = edition.get("block_code"), name = edition.get("block"))
    #            block.editions.append(db_edition)
    #            session.add(block)
    #    if edition.get("parent_set_code") is not None:
    #        if db_edition.id is None:
    #            session.commit()
    #        parent_edition_rel[db_edition.id] = edition.get("parent_set_code")


    #for ed, parent in parent_edition_rel.items():
    #    child_edition = session.query(Edition).get(ed)
    #    parent_edition = session.query(Edition).filter_by(code = parent).one()
    #    parent_edition.child_editions.append(child_edition)

    #session.commit()
    
    #cards_online = get_scryfall_cards()
    #with open("cards.json", "w") as f:
    #    json.dump(cards_online, f)

    with open("cards.json", "r") as f:
        cards = json.load(f)

    for idx, e in enumerate(cards):
        got = ["object", "card_faces", "set", "set_name", "set_type", "set_uri", "set_search_uri", "scryfall_set_uri", "related_uris"]
        def get(string):
            g = e.get(string)
            got.append(string)
            return g

        def lget(string):
            g = e.get(string)
            got.append(string)
            return g if g is not None else []

        def iget(string):
            g = e.get(string)
            got.append(string)
            return int(g) if g is not None and g.isdigit() else None

        try:
            card = session.query(Card).filter(Card.oracle_id == e.get('oracle_id')).one()
            got += ['oracle_id', 'layout', 'cmc', 'power', 'colors', 'legalities', 'rulings_uri']
            got += ['name', 'type_line', 'color_indicator', 'color_identity', 'prints_search_uri']
            got += ['mana_cost', 'reserved', 'toughness', 'oracle_text', 'edhrec_rank', 'loyalty']
            got += ['life_modifier', 'hand_modifier']
        except:
            card = Card( oracle_id = get('oracle_id')
                       , prints_search_uri = get("prints_search_uri") 
                       , rulings_uri = get("rulings_uri")
                       , cmc = get("cmc")
                       , reserved = get("reserved")
                       , type_line = get("type_line")
                       , name = get("name")
                       , layout = get("layout")
                       , mana_cost = get("mana_cost")
                       , power_str = get("power")
                       , power = iget("power")
                       , toughness_str = get("toughness")
                       , toughness = iget("toughness")
                       , colors = lget("colors")
                       , color_identity = lget("color_identity")
                       , color_indicator = lget("color_indicator")
                       , legalities = lget("legalities")
                       , oracle_text = get("oracle_text")
                       , edhrec_rank = get("edhrec_rank")
                       , loyalty = iget('loyalty')
                       , loyalty_str = get("loyalty")
                       , life_modifier = get("life_modifier")
                       , hand_modifier = get("hand_modifier")
                       )
            session.add(card)
        try:
            base_card = session.query(BaseCard).join(Edition)\
                    .filter(Edition.code == e['set'])\
                    .filter(BaseCard.collector_number_str == e["collector_number"]).one()
            got += ['tcgplayer_id']
            got += ['frame_effects', "watermark"]
        except NoResultFound:
            edition = session.query(Edition).filter(Edition.code == e.get("set")).one()
            base_card = BaseCard( card = card
                                , edition = edition                                
                                , multiverse_ids = lget("multiverse_ids")
                                , released_at = datetime.datetime.strptime(get("released_at"), "%Y-%m-%d")
                                , highres_image = get("highres_image")
                                , has_foil = get("foil")
                                , has_nonfoil = get("nonfoil")
                                , games = get("games")                       
                                , oversized = get("oversized")
                                , promo = get("promo")
                                , promo_types = lget("promo_types")
                                , reprint = get("reprint")
                                , variation = get("variation")
                                , collector_number = get("collector_number")
                                , digital = get("digital")
                                , rarity = get("rarity")
                                , card_back_id = get("card_back_id")
                                , artist = get("artist")
                                , artist_ids = [UUID(u) for u in get("artist_ids")] if get("artist_ids") is not None else []
                                , illustration_id = get("illustration_id")
                                , border_color = get("border_color")
                                , frame = get("frame")
                                , full_art = get("full_art")
                                , textless = get("textless")
                                , booster = get("booster")
                                , story_spotlight = get("story_spotlight")
                                , flavor_text = get("flavor_text")
                                , tcgplayer_id = get("tcgplayer_id")
                                , frame_effects = lget("frame_effects")
                                , watermark = get("watermark")
                                )
            session.add(base_card)
        try:
            printing = session.query(Printing).filter(Printing.scryfall_id == UUID(e.get("id"))).one()
            print(f"({idx + 1}/{len(cards)}) (X) {printing.base_card.card.name}, {printing.base_card.edition.code}, {printing.base_card.collector_number}, {printing.lang}")        
            got += ['id', 'lang', 'uri', 'scryfall_uri', 'image_uris']
            got += ['printed_name', 'printed_text', 'printed_type_line']
        except NoResultFound:
            printing = Printing( base_card=base_card
                               , scryfall_id = UUID(get("id"))
                               , lang = get("lang")
                               , scryfall_uri = get("scryfall_uri")
                               , uri = get("uri")
                               , image_uri_png = get("image_uris").get("png") if get("image_uris") is not None else None
                               , image_uri_border_crop = get("image_uris").get("border_crop") if get("image_uris") is not None else None
                               , image_uri_art_crop = get("image_uris").get("art_crop") if get("image_uris") is not None else None
                               , image_uri_large = get("image_uris").get("large") if get("image_uris") is not None else None
                               , image_uri_normal = get("image_uris").get("normal") if get("image_uris") is not None else None
                               , image_uri_small = get("image_uris").get("small") if get("image_uris") is not None else None
                               , printed_name = get("printed_name")
                               , printed_text = get("printed_text")
                               , printed_type_line = get("printed_type_line")
                               )
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
