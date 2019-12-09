from . import create_dict
from .card import get_card_from_sf
from ..model import CardFacePrinting, CardFaceBase, CardFace


def get_db_card_face(name, session):
    return session.query(CardFace).filter(CardFace.name == name).first()

def get_db_card_face_from_sf(face, session):
    return get_db_card_face(face["name"], session)
    #faces = []
    #if "card_faces" in e:
    #    for face in e["card_faces"]:
    #        faces.append(get_db_card_face(face["name"], session))
    #return faces

def get_card_face_from_sf(face, e, session):
    card_face = get_db_card_face_from_sf(face, session)
    if card_face is not None:
        return card_face
    card_face = add_card_face(face, e, session)
    session.commit()
    return card_face

def add_card_face(face, e, session):
    card = get_card_from_sf(e, session)
    card_face  = create_card_face(face, card)
    session.add(card_face)
    return card_face
    
def create_card_face(face, card):
    fields = ["name", "mana_cost", "type_line", "oracle_text"]
    fields_int = ["power", "toughness"]
    lists=["colors", "color_indicator"]
    fields_uuid = []
    renames = {"power": "power_str", "toughness": "toughness_str"}
    if type(card) is int:
        custom = {"card_id": card}
    else:
        custom = {"card": card}

    dict_all = create_dict(face, fields=fields, lists=lists, fields_int=fields_int, fields_uuid=fields_uuid, renames=renames, custom=custom)

    return CardFace(**dict_all)

def create_card_face_printing(face, card_face_base, printing):
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
    custom = {}
    if type(card_face_base) is int:
        custom["card_face_base_id"] = card_face_base
    else:
        custom["card_face_base"] = card_face_base
    if type(printing) is int:
        custom["card_printing_id"] = printing
    else:
        custom["card_printing"] = printing

    dict_all = create_dict(face, fields=fields, objects=objects, custom=custom)

    return CardFacePrinting(**dict_all)


def makeCardFacePrinting(e, card_base_face, printing, session):
    card_face_printing = session.query(CardFacePrinting)\
        .filter(CardFacePrinting.card_face_base == card_base_face)\
        .filter(CardFacePrinting.card_printing == printing).first()
    if card_face_printing is None:
        card_face_printing = create_card_face_printing(e, card_base_face, printing)
        session.add(card_face_printing)
    return card_face_printing
    

def create_card_face_base(face, card_face, basecard):
    fields = ["artist", "flavor_text", "watermark"]
    fields_uuid = ["artist_id", "illustration_id"]
    custom = {}
    if type(card_face) is int:
        custom["card_face_id"] = card_face
    else:
        custom["card_face"] = card_face
    if type(basecard) is int:
        custom["basecard_id"] = basecard
    else:
        custom["basecard"] = basecard

    dict_all = create_dict(face, fields=fields, fields_uuid=fields_uuid, custom = custom)

    return CardFaceBase(**dict_all)


def makeCardBaseFace(face, card_face, basecard, session):
    card_base_face = session.query(CardFaceBase)\
            .filter(CardFaceBase.card_face == card_face)\
            .filter(CardFaceBase.basecard == basecard).first()
    if card_base_face is None:
        card_base_face = create_card_face_base(face, card_face, basecard)
        session.add(card_base_face)
    return card_base_face

    


