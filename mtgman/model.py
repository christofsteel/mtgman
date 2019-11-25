from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Table, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Block(Base):
    __tablename__ = "block"
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)

class Edition(Base):
    __tablename__ = "edition"
    id = Column(Integer, primary_key=True)
    scryfall_id = Column(UUIDType, nullable=False)
    code = Column(String, nullable=False, unique=True)
    mtgo_code = Column(String)
    tcgplayer_id = Column(Integer)
    name = Column(String, nullable=False, unique=True)
    set_type = Column(String, nullable=False)
    released_at = Column(Date)
    block_id = Column(Integer, ForeignKey("block.id"))
    block = relationship("Block", backref="editions")
    parent_set_id = Column(Integer, ForeignKey("edition.id"))
    card_count = Column(Integer, nullable=False)
    digital = Column(Boolean, nullable=False)
    foil_only = Column(Boolean, nullable=False)
    scryfall_uri = Column(String, nullable=False)
    uri = Column(String, nullable=False)
    icon_svg_uri = Column(String, nullable=False)
    search_uri = Column(String, nullable=False)
    child_editions = relationship("Edition", backref=backref("parent_edition", remote_side=[id]))

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
    edition_card_id = Column(Integer, ForeignKey("basecard.id"))
    scryfall_id = Column(UUIDType, nullable=False)
    lang = Column(String)
    scryfall_uri = Column(String, nullable=False)
    uri = Column(String, nullable=False)
    
class FrameEffects(Base):
    __tablename__ = "frame_effects"
    id = Column(Integer, primary_key=True)
    effect = Column(String, nullable=False)
    bcard_id = Column(Integer, ForeignKey("basecard.id"), nullable=False)
    bcard = relationship("BaseCard", backref="frame_effects")

class Games(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    game = Column(String, nullable=False)
    bcard_id = Column(Integer, ForeignKey("basecard.id"), nullable=False)
    bcard = relationship("BaseCard", backref="frame_effects")

class BaseCard(Base):
    __tablename__ = "basecard"
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("card.id"))
    edition_id = Column(Integer, ForeignKey("edition.id"))
    arena_id = Column(Integer)
    mtgo_id = Column(Integer)
    mtgo_foil_id = Column(Integer)
    multiverse_id = Column(Integer)
    tcgplayer_id = Column(Integer)
    has_foil = Column(Boolean, nullable=False)
    has_nonfoil = Column(Boolean, nullable=False)
    oversized = Column(Boolean, nullable=False)
    artist = Column(String)
    booster = Column(Boolean, nullable=False)
    border_color = Column(String, nullable=False)
    card_back_id = Column(UUIDType, nullable=False) 
    collector_number = Column(Integer, nullable=False)
    collector_number_str = Column(String, nullable=True)
    digital = Column(Boolean, nullable=False)
    flavor_text = Column(String)
    frame = Column(String, nullable=False)
    full_art = Column(String, nullable=False)
    highres_image = Column(Boolean, nullable=False)
    illustration_id = Column(UUIDType)
    


class Colors(Base):
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True)
    color = Column(String, nullable=False)
    card_id = Column(Integer, ForeignKey("card.id"))
    color_of = relationship("Card", backref="colors")

class ColorIDs(Base):
    __tablename__ = "color_identity"
    id = Column(Integer, primary_key=True)
    color = Column(String, nullable=False)
    card_id = Column(Integer, ForeignKey("card.id"))
    color_of = relationship("Card", backref="color_identity")

class ColorInds(Base):
    __tablename__ = "color_indicator"
    id = Column(Integer, primary_key=True)
    color = Column(String, nullable=False)
    card_id = Column(Integer, ForeignKey("card.id"))
    color_of = relationship("Card", backref="color_indicator")

class Card(Base):
    __tablename__ = "card"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    oracle_id = Column(UUIDType, nullable=False)
    prints_search_uri = Column(String, nullable=False)
    rulings_uri = Column(String, nullable=False)
    all_parts = relationship("Card", secondary="part_of", backref=backref("part_of", remote_side=[id]))
    face_of_id = Column(Integer)
    face_of = relationship("Card", backref=backref("card_faces", local_side=[face_of_id], remote_side=[id]))
    cmc = Column(Integer, nullable=False)
    cmc_str = Column(String)
    edhrec_rank = Column(Integer)
    hand_modifier = Column(String)
    layout = Column(String)
    life_modifier = Column(String)
    loyality = Column(Integer)
    loyality_str = Column(String)
    mana_costs = Column(String)
    name = Column(String)
    oracle_text = Column(String)
    power = Column(Integer)
    power_str = Column(String)
    reserved = Column(Boolean, nullable=False)
    toughness = Column(Integer)
    toughness_str = Column(String)
    type_line = Column(String, nullable=False)
    
    
class Legality(Base):
    __tablename__ = "legality"
    id = Column(Integer, primary_key = True)
    legality = Column(String, nullable = False)
    card_id = Column(Integer, ForeignKey("card.id"))
    cards = relationship("Card", backref="legality")


part_of = Table('part_of', Base.metadata,
        Column('card_id1', Integer, ForeignKey('card.id')),
        Column('card_id2', Integer, ForeignKey('card.id'))
)

