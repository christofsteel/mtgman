from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from inspect import currentframe
from sqlalchemy.inspection import inspect
import traceback
from IPython.core.debugger import set_trace

Base = declarative_base()

arrays = {}


def makeArray(foreign_key, name, dict_or_type, foreign_class_f = lambda:traceback.extract_stack()[-3][2]):

    def init(self, value):
        self.value = value

    backref_id = currentframe().f_back.f_code.co_names[-1] + "_id"
    foreign_class = foreign_class_f()
    if type(dict_or_type) is dict:
        arrays[name] = type(name, (Base,), {
            "__tablename__": name,
            "id": Column(Integer, primary_key=True),
            "remote_id": Column(Integer, ForeignKey(foreign_key)),
            **dict_or_type
            })
    else:
        arrays[name] = type(name, (Base,), {
            "__tablename__": name,
            "id": Column(Integer, primary_key=True),
            "remote_id": Column(Integer, ForeignKey(foreign_key)),
            "value": Column(dict_or_type),
            "remote": relationship(foreign_class, backref=backref_id),
            "__init__": init
            })
    return association_proxy(backref_id, "value")
        
    

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fav_nrs = makeArray("person.id", "FavNr2", Integer)
    #fav_nrs = association_proxy("fav_nrs_id", "nr")
    #fav_nrs_id = relationship("FavNr")

#class FavNr(Base):
#    __tablename__ = 'fav_nrs'
#    id = Column(Integer, primary_key=True)
#    nr = Column(Integer)
#    person_id = Column(Integer, ForeignKey("person.id"))
#    person = relationship("Person")
#
#    def __init__(self, nr):
#        self.nr = nr



engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

p = Person(name = "Hans")
#p.fav_nrs.append(3)
#p.fav_nrs.append(4)
#p.fav_nrs.append(5)
#p.fav_nrs.append(6)

#import inspect, gc
#
#def printVarName():
#    f = inspect.currentframe().f_back.f_code.co_names[-1]
#    print(f)
#    return f
#
#a = printVarName()
