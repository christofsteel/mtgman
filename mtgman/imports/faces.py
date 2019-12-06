from . import create_dict
from ..model import CardFacePrinting, CardFaceBase, CardFace

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

    dict_all = create_dict(e, fields=fields, objects=objects, custom=custom)
    card_face_printing = session.query(CardFacePrinting)\
        .filter(CardFacePrinting.card_face_base == card_base_face)\
        .filter(CardFacePrinting.card_printing == printing).first()

    if card_face_printing is None:
        card_face_printing = CardFacePrinting(**dict_all)
        session.add(card_face_printing)

def makeCardBaseFace(face, card_face, basecard, session):
    fields = ["artist", "flavor_text", "watermark"]
    fields_uuid = ["artist_id", "illustration_id"]
    custom = {"card_face" : card_face, "basecard": basecard}

    dict_all = create_dict(face, fields=fields, fields_uuid=fields_uuid, custom = custom)

    card_base_face = session.query(CardFaceBase)\
            .filter(CardFaceBase.card_face == card_face)\
            .filter(CardFaceBase.basecard == basecard).first()

    if card_base_face is None:
        card_base_face = CardFaceBase(**dict_all)
        session.add(card_base_face)

    return card_base_face

def makeCardFace(face, card, session):
    fields = ["name", "mana_cost", "type_line", "oracle_text"]
    fields_int = ["power", "toughness"]
    lists=["colors", "color_indicator"]
    fields_uuid = []
    renames = {"power": "power_str", "toughness": "toughness_str"}
    custom = {"card": card}

    dict_all = create_dict(face, fields=fields, lists=lists, fields_int=fields_int, fields_uuid=fields_uuid, renames=renames, custom=custom)

    card_face = session.query(CardFace).filter(CardFace.name == face["name"]).first()

    if card_face is None:
        card_face = CardFace(**dict_all)
        session.add(card_face)

    return card_face
    

def fillCardFaces(e, printing, session):
    if "card_faces" in e.keys():
        for face in e["card_faces"]:
            card_face = makeCardFace(face, printing.base_card.card, session)
            card_base_face = makeCardBaseFace(face, card_face, printing.base_card, session)
            makeCardFacePrinting(face, card_base_face, printing, session)
            session.commit()


