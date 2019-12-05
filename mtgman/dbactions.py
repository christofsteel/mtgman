import scrython
from tqdm import tqdm
import requests
from io import BytesIO
import json
import tempfile

from .parser import parser
from .model import Card

def complete_scrython_data(scrython_object):
    data = scrython_object.scryfallJson["data"]

    if "total_cards" in scrython_object.scryfallJson and scrython_object.scryfallJson["total_cards"] > 2000:
        yn = input(f"Your query has {scrython_object.scryfallJson['total_cards']} results. Are you sure you want to continue [y/N]? ")
        if yn.lower() != 'y':
            return []

    #suffix = f"{page:04d}"
    #with tempfile.NamedTemporaryFile(prefix=suffix, delete=False) as tmpf:
    #    tmpfiles.append(tmpf.name)
    #    json.dump(data, tmpf)

    while scrython_object.scryfallJson["has_more"]:
        print(scrython_object.scryfallJson["next_page"])
        scrython_object = scrython.foundation.FoundationObject(scrython_object.scryfallJson["next_page"], override=True)
        data += scrython_object.scryfallJson["data"]

        #page = page + 1
        #suffix = f"{page:04d}"
        #with tempfile.NamedTemporaryFile(prefix=suffix, delete=False) as tmpf:
        #    tmpfiles.append(tmpf.name)
        #    json.dump(data, tmpf)

    return data

def get_scryfall_cards(query):
    return complete_scrython_data(scrython.Search(q=query, unique="prints", include_extras=True, include_multilingual=True))

def get_scryfall_sets():
    return complete_scrython_data(scrython.foundation.FoundationObject("sets?"))

def find_edition(json, code):
    for e in json:
        if e.get("code") == code:
            return e
    raise RuntimeError(f"did not find {code} in {[e['code'] for e in json]}")

def find_by_scryfall_id(all_cards, id):
    card = all_cards.get(id)
    if card is not None:
        return card
    print(f"Failed to find card: {id}, try online.")
    return scrython.cards.Id(id = id).scryfallJson

def find_first_by_name(all_cards, name):
    for e in all_cards.values():
        if e.get("name") == name:
            return e
    raise RuntimeError(f"did not find card: {id}")

def find_all_by_name(all_cards, name):
    l = []
    for e in all_cards.values():
        if e.get("name") == name:
            l.append(e)
    return l


def dbquery(query, session):
    parsed_query = parser.parse(query)
    for res in session.query(Card).filter(parsed_query.dbfilter()).all():
        print(f"{res.name}, {res.mana_cost}, {res.type_line}")
