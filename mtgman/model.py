from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Table, Float, Numeric
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from inspect import currentframe

Base = declarative_base()

scalars = {}

def makeScalar(foreign_key, dict_or_type, name=None, foreign_class=None, backref_id=None):

    def init(self, value):
        self.value = value

    foreign_class = currentframe().f_back.f_code.co_name if foreign_class is None else foreign_class
    if backref_id is None:
        if name is None:
            backref_id = currentframe().f_back.f_code.co_names[-1] + "_id"
        else:
            backref_id = name + "_id"

    if name is None:
        name = currentframe().f_back.f_code.co_names[-1]

    if type(dict_or_type) is dict:
        scalars[name] = type(name, (Base,), {
            "__tablename__": name,
            "id": Column(Integer, primary_key=True),
            "remote_id": Column(Integer, ForeignKey(foreign_key)),
            **dict_or_type
            })
        return relationship(name, backref="remote")
    else:
        scalars[name] = type(name, (Base,), {
            "__tablename__": name,
            "id": Column(Integer, primary_key=True),
            "remote_id": Column(Integer, ForeignKey(foreign_key)),
            "value": Column(dict_or_type),
            "remote": relationship(foreign_class, backref=backref_id),
            "__init__": init
            })
        return association_proxy(backref_id, "value")

class Block(Base):
    __tablename__ = "block"
    code = Column(String, nullable=False, unique=True, primary_key=True)
    name = Column(String, nullable=False)

class Edition(Base):
    __tablename__ = "edition"
    code = Column(String, nullable=False, unique=True, primary_key=True)
    scryfall_id = Column(UUIDType, nullable=False)
    mtgo_code = Column(String)
    tcgplayer_id = Column(Integer)
    name = Column(String, nullable=False, unique=True)
    set_type = Column(String, nullable=False)
    released_at = Column(Date)
    block_code = Column(Integer, ForeignKey("block.code"))
    block = relationship("Block", backref="editions")
    parent_set_code = Column(Integer, ForeignKey("edition.code"))
    card_count = Column(Integer, nullable=False)
    digital = Column(Boolean, nullable=False)
    foil_only = Column(Boolean, nullable=False)
    scryfall_uri = Column(String, nullable=False)
    uri = Column(String, nullable=False)
    icon_svg_uri = Column(String, nullable=False)
    search_uri = Column(String, nullable=False)
    child_editions = relationship("Edition", backref=backref("parent_edition", remote_side=[code]))

class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(Integer)
    parent_id = Column(Integer, ForeignKey("collection.id"))
    child = relationship("Collection", backref=backref("parent", remote_side=[id]))



class collected(Base):
    __tablename__ = "collected"
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collection.id"))
    ccard_id = Column(Integer, ForeignKey("collectioncard.id"))
    count = Column(Integer)
    

class CollectionCard(Base):
    __tablename__ = "collectioncard"
    id = Column(Integer, primary_key=True)
    printing_id = Column(Integer, ForeignKey("printing.id"))
    foil = Column(Boolean, nullable=False)


class Printing(Base):
    __tablename__ = "printing"
    id = Column(Integer, primary_key=True)
    base_card_id = Column(Integer, ForeignKey("basecard.id"), nullable=False)
    base_card = relationship("BaseCard", backref="printings")
    scryfall_id = Column(UUIDType, unique=True, nullable=False)
    lang = Column(String)
    scryfall_uri = Column(String, nullable=False)
    uri = Column(String, nullable=False)
    image_uri_png = Column(String)
    image_uri_border_crop = Column(String)
    image_uri_art_crop = Column(String)
    image_uri_large = Column(String)
    image_uri_normal = Column(String)
    image_uri_small = Column(String)
    printed_name = Column(String)
    printed_text = Column(String)
    printed_type_line = Column(String)

    
#class FrameEffects(Base):
#    __tablename__ = "frame_effects"
#    id = Column(Integer, primary_key=True)
#    effect = Column(String, nullable=False)
#    bcard_id = Column(Integer, ForeignKey("basecard.id"), nullable=False)
#    bcard = relationship("BaseCard", backref="frame_effects")
#
#class Games(Base):
#    __tablename__ = "games"
#    id = Column(Integer, primary_key=True)
#    game = Column(String, nullable=False)
#    bcard_id = Column(Integer, ForeignKey("basecard.id"), nullable=False)
#    bcard = relationship("BaseCard", backref="frame_effects")



class BaseCard(Base):
    __tablename__ = "basecard"
    __table_args__ = (UniqueConstraint('collector_number_str', 'edition_code', name='set_cn_uc'),)
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("card.id"), nullable=False)
    card = relationship("Card", backref="base_cards")
    edition_code = Column(Integer, ForeignKey("edition.code"))
    edition = relationship("Edition", backref="cards")
    arena_id = Column(Integer)
    mtgo_id = Column(Integer)
    mtgo_foil_id = Column(Integer)
    multiverse_ids = makeScalar("basecard.id", Integer, name="multiverse_ids")
    tcgplayer_id = Column(Integer)
    has_foil = Column(Boolean, nullable=False)
    has_nonfoil = Column(Boolean, nullable=False)
    oversized = Column(Boolean, nullable=False)
    artist = Column(String)
    artist_ids = makeScalar("basecard.id", UUIDType, name="artist_ids")
    booster = Column(Boolean, nullable=False)
    border_color = Column(String, nullable=False)
    card_back_id = Column(UUIDType, nullable=False) 
    collector_number = Column(Integer, nullable=False)
    collector_number_str = Column(String, nullable=True)
    digital = Column(Boolean, nullable=False)
    flavor_text = Column(String)
    frame = Column(String, nullable=False)
    frame_effects = makeScalar("basecard.id", String, name="frame_effects")
    full_art = Column(String, nullable=False)
    games = makeScalar("basecard.id", String, name="games")
    highres_image = Column(Boolean, nullable=False)
    illustration_id = Column(UUIDType)
    price_usd = Column(Float)
    price_usd_foil = Column(Float)
    price_eur = Column(Float)
    price_tix = Column(Float)
    promo = Column(Boolean, nullable=False)
    promo_types = makeScalar("basecard.id", String, name="promo_type")
    #purchase_uris
    rarity = Column(String, nullable=False)
    #related_uris
    released_at = Column(Date, nullable=False)
    reprint = Column(Boolean, nullable=False)
    #scryfall_set_uri
    #set_name
    #set_search_uri
    #set_type
    #set_uri
    #set
    story_spotlight = Column(Boolean, nullable=False)
    textless = Column(Boolean, nullable=False)
    variation = Column(Boolean, nullable=False)
    variation_of = Column(UUIDType) # sqlid
    watermark = Column(String)
    previewed_at = Column(Date)
    preview_source_uri = Column(String)
    preview_source = Column(String)
    
    

    



#class Colors(Base):
#    __tablename__ = "colors"
#    id = Column(Integer, primary_key=True)
#    color = Column(String, nullable=False)
#    card_id = Column(Integer, ForeignKey("card.id"))
#    color_of = relationship("Card", backref="colors")
#
#class ColorIDs(Base):
#    __tablename__ = "color_identity"
#    id = Column(Integer, primary_key=True)
#    color = Column(String, nullable=False)
#    card_id = Column(Integer, ForeignKey("card.id"))
#    color_of = relationship("Card", backref="color_identity")
#
#class ColorInds(Base):
#    __tablename__ = "color_indicator"
#    id = Column(Integer, primary_key=True)
#    color = Column(String, nullable=False)
#    card_id = Column(Integer, ForeignKey("card.id"))
#    color_of = relationship("Card", backref="color_indicator")

#part_of = Table('part_of', Base.metadata,
#        Column('card_id1', Integer, ForeignKey('card.id')),
#        Column('card_id2', Integer, ForeignKey('card.id'))
#)


class Card(Base):
    __tablename__ = "card"
    id = Column(Integer, primary_key=True)
    oracle_id = Column(UUIDType, unique=True, nullable=False)
    prints_search_uri = Column(String, nullable=False)
    rulings_uri = Column(String, nullable=False)
    #all_parts = relationship("Card", secondary="part_of", backref=backref("part_of", remote_side=[id]), primaryjoin=id==part_of.c.card_id1, secondaryjoin=part_of.c.card_id2==id)
    #face_of_id = Column(Integer)
    #face_of = relationship("Card", backref=backref("card_faces", local_side=[face_of_id], remote_side=[id]))
    colors = makeScalar("card.id", String, name="colors")
    color_identity = makeScalar("card.id", String, name="color_identity")
    color_indicator = makeScalar("card.id", String, name="color_indicator")
    cmc = Column(Float, nullable=False)
    edhrec_rank = Column(Integer)
    hand_modifier = Column(String)
    layout = Column(String)
    legalities = makeScalar("card.id", String, name="legalities")
    life_modifier = Column(String)
    loyalty = Column(Integer)
    loyalty_str = Column(String)
    mana_cost = Column(String)
    name = Column(String)
    oracle_text = Column(String)
    power = Column(Integer)
    power_str = Column(String)
    reserved = Column(Boolean, nullable=False)
    toughness = Column(Integer)
    toughness_str = Column(String)
    type_line = Column(String, nullable=False)

class CardFacePrinting(Base):
    __tablename__ = "card_face_printing"
    __table_args__ = (UniqueConstraint('card_face_base_id', 'card_printing_id', name='face_for_printing_uc'),)

    id = Column(Integer, primary_key=True)
    card_face_base_id = Column(Integer, ForeignKey("card_face_base.id"), nullable=False)
    card_face_base = relationship("CardFaceBase", backref="card_face_printings")
    card_printing_id = Column(Integer, ForeignKey("printing.id"), nullable=False)
    card_printing = relationship("Printing", backref="faces")

    image_uri_png = Column(String)
    image_uri_border_crop = Column(String)
    image_uri_art_crop = Column(String)
    image_uri_large = Column(String)
    image_uri_normal = Column(String)
    image_uri_small = Column(String)
    printed_name = Column(String)
    printed_text = Column(String)
    printed_type_line = Column(String)


class CardFaceBase(Base):
    __tablename__ = "card_face_base"    
    __table_args__ = (UniqueConstraint('card_face_id', 'basecard_id', name='face_for_base_uc'),)
     
    id = Column(Integer, primary_key=True)
    card_face_id = Column(Integer, ForeignKey("card_face.id"))
    card_face = relationship("CardFace", backref="card_face_bases")
    basecard_id = Column(Integer, ForeignKey("basecard.id"))
    basecard = relationship("BaseCard", backref="faces")

    artist = Column(String)
    artist_id = Column(UUIDType)
    illustration_id = Column(UUIDType)
    flavor_text = Column(String)
    watermark = Column(String)

class CardFace(Base):
    __tablename__ = "card_face"

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    card = relationship("Card", backref="faces")

    name = Column(String, nullable=False, unique=True)
    mana_cost = Column(String, nullable=False)
    type_line = Column(String, nullable=False)
    oracle_text = Column(String, nullable=False)
    power = Column(Integer)
    power_str = Column(String)
    toughness = Column(Integer)
    toughness_str = Column(String)
    color_indicator = makeScalar("card_face.id", String, name="color_indicator_face")
    colors = makeScalar("card_face.id", String, name="colors_face")
    loyalty = Column(Integer)
    loyalty_str = Column(String)
    type_line = Column(String)

    


class Legality(Base):
    __tablename__ = "legality"
    legal_id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("card.id"), nullable=False)
    fmt = Column(String, nullable=False)
    status = Column(String, nullable=False)
    card = relationship(Card, backref="legalities")

class Parts(Base):
    __tablename__ = 'part_of'
    card_id1 = Column(Integer, ForeignKey('card.id'), primary_key=True)
    card_id2 = Column(Integer, ForeignKey('card.id'), primary_key=True)
    card_component = Column(String)
    card1 = relationship(Card, backref="all_parts", foreign_keys=card_id1)
    card2 = relationship(Card, backref="part_of", foreign_keys=card_id2)
    
    
#class Legality(Base):
#    __tablename__ = "legality"
#    id = Column(Integer, primary_key = True)
#    legality = Column(String, nullable = False)
#    card_id = Column(Integer, ForeignKey("card.id"))
#    cards = relationship("Card", backref="legality")


