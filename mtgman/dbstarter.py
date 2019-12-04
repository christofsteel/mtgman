from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .imports import import_sets, import_cards
from .dbactions import dbquery
from .model import Base

engine = create_engine("sqlite:///test.db", echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)
session = Session()
