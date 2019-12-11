from tqdm import tqdm
from sqlalchemy.exc import IntegrityError

from ..model import Card, BaseCard, Printing, CardFace, CardFaceBase, CardFacePrinting
from .scryfall import get_scryfall_cards, get_scryfall_bulk
from .printing import printing_prepare_bulk_add, printing_bulk_add,  get_db_printing_from_sf, fill_card_faces, create_printing
from .basecard import base_card_prepare_bulk_add, base_card_bulk_add, create_base_card, get_db_base_card_from_sf
from .faces import create_card_face, create_card_face_base, create_card_face_printing
from .card import card_prepare_bulk_add, card_bulk_add, create_card

def import_cards_from_bulk(level, session):
    cards = get_scryfall_bulk(level)
    return import_cards(cards,session)

def import_cards_from_query(query, session):
    cards = get_scryfall_cards(query)
    return import_cards(cards,session)

def import_cards(cards, session):
    new_cards = {}
    new_base_cards = {}
    new_printings = {}
    new_card_faces = {}
    new_card_faces_base = {}
    new_card_faces_printing = {}
    old_cards = {card[0]: card[1] for card in session.query(Card.name, Card.id)}
    old_base_cards = {(card[0], card[1]): card[2] for card in session.query(BaseCard.collector_number_str ,BaseCard.edition_code, BaseCard.id)}
    old_printings = {(card[0], card[1], card[2]): card[3] for card in session.query(BaseCard.collector_number_str, BaseCard.edition_code, Printing.lang, Printing.id).join(Printing)}
    old_card_faces = {face[0]: face[1] for face in session.query(CardFace.name, CardFace.name)}
    old_card_faces_base = {(face[0], face[1]): face[2] for face in session.query(CardFaceBase.card_face_id, CardFaceBase.basecard_id, CardFaceBase.id)}
    old_card_faces_printing = {(face[0], face[1]): face[2] for face in session.query(CardFacePrinting.card_face_base_id, CardFacePrinting.card_printing_id, CardFacePrinting.id)}

    for card in tqdm(cards, desc="Importing oracle cards", unit="cards"):
        if card["name"] in old_cards:
            continue
        elif card["name"] in new_cards:
            continue
        else:
            new_card = create_card(card)
            new_cards[card["name"]] = new_card
    session.bulk_save_objects(list(new_cards.values()), return_defaults=True)
    session.commit()

    for card in tqdm(cards, desc="Importing base cards", unit="cards"):
        if (card["collector_number"], card["set"]) in old_base_cards:
            continue
        elif (card["collector_number"], card["set"]) in new_base_cards:
            continue
        else:
            card_id = old_cards[card["name"]] if card["name"] in old_cards else new_cards[card["name"]].id
            new_base_card = create_base_card(card, card_id, card["set"])
            new_base_cards[card["collector_number"], card["set"]] = new_base_card

    session.bulk_save_objects(list(new_base_cards.values()), return_defaults=True)
    session.commit()

    for card in tqdm(cards, desc="Importing printings", unit="cards"):
        if (card["collector_number"], card["set"], card["lang"]) in old_printings:
            continue
        elif (card["collector_number"], card["set"], card["lang"]) in new_printings:
            continue
        else:
            key = (card["collector_number"], card["set"])
            base_card_id = old_base_cards[key]\
                    if key in old_base_cards else new_base_cards[key].id
            new_printing = create_printing(card, base_card_id) 
            new_printings[card["collector_number"],card["set"], card["lang"]] = new_printing            
    session.bulk_save_objects(list(new_printings.values()), return_defaults=True)
    session.commit()

    for card in tqdm(cards, desc="Importing oracle faces", unit="cards"):
        if (card["collector_number"], card["set"], card["lang"]) in old_printings:
            continue
        elif "card_faces" in card.keys():
            card_id = old_cards[card["name"]] if card["name"] in old_cards else new_cards[card["name"]].id
            
            for face in card["card_faces"]:
                if face["name"] in old_card_faces:
                    continue
                card_face = create_card_face(face, card_id) 
                new_card_faces[face["name"]] = card_face
    session.bulk_save_objects(list(new_card_faces.values()), return_defaults=True)
    session.commit()

    for card in tqdm(cards, desc="Importing base faces", unit="cards"):
        if (card["collector_number"], card["set"], card["lang"]) in old_printings:
            continue
        elif "card_faces" in card.keys():
            key = (card["collector_number"], card["set"])
            base_card_id = old_base_cards[key]\
                    if key in old_base_cards else new_base_cards[key].id

            for face in card["card_faces"]:
                card_face_id = old_card_faces[face["name"]] if face["name"] in old_card_faces else new_card_faces[face["name"]].id
                if (card_face_id, base_card_id) in old_base_cards:
                    continue
                card_face_base = create_card_face_base(face, card_face_id , base_card_id)
                new_card_faces_base[(card_face_id, base_card_id)] = card_face_base
    session.bulk_save_objects(list(new_card_faces_base.values()), return_defaults=True)
    session.commit()
                
    for card in tqdm(cards, desc="Importing face printings", unit="cards"):
        if (card["collector_number"], card["set"], card["lang"]) in old_printings:
            continue
        elif "card_faces" in card.keys():
            key = (card["collector_number"], card["set"], card["lang"])
            printing_id = old_printings[key]\
                    if key in old_printings else new_printings[key].id
            key = (card["collector_number"], card["set"])
            base_card_id = old_base_cards[key]\
                    if key in old_base_cards else new_base_cards[key].id

            for face in card["card_faces"]:
                card_face_id = old_card_faces[card["name"]] if face["name"] in old_card_faces else new_card_faces[face["name"]].id
                card_face_base_id = old_card_faces_base[(card_face_id, base_card_id)]\
                        if (card_face_id, base_card_id) in old_card_faces_base else new_card_faces_base[(card_face_id, base_card_id)].id
                if (card_face_base_id, printing_id) in old_card_faces_printing:
                    continue
                card_face_printing = create_card_face_printing(face, card_face_base_id, printing_id)
                new_card_faces_printing[(card_face_base_id, printing_id)] = card_face_printing
    session.bulk_save_objects(list(new_card_faces_printing.values()), return_defaults=True)
    session.commit()
