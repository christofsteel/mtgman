import scrython
import urllib
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from tqdm import tqdm

def load_with_bar(url):
    rq = requests.get(url, stream=True)
    content_length = int(rq.headers.get("content-length"))

    executor = ThreadPoolExecutor()
    data = executor.submit(rq.json)
    pbar = tqdm(total=content_length, unit='B', unit_scale=True, desc=url.split('/')[-1])
    pos = 0
    while not data.done():
        time.sleep(0.01)
        newpos = rq.raw.tell()
        pbar.update(newpos - pos)
        pos = newpos
    return data.result()

def complete_scrython_data(scrython_object):
    data = scrython_object.scryfallJson["data"]

    if "total_cards" in scrython_object.scryfallJson and scrython_object.scryfallJson["total_cards"] > 2000:
        yn = input(f"Your query has {scrython_object.scryfallJson['total_cards']} results. Are you sure you want to continue [y/N]? ")
        if yn.lower() != 'y':
            return []
    page = 1
    while scrython_object.scryfallJson["has_more"]:
        print(f"[{page}]", end='', flush=True)
        scrython_object = scrython.foundation.FoundationObject(scrython_object.scryfallJson["next_page"], override=True)
        data += scrython_object.scryfallJson["data"]
        page += 1
    print(f"[{page}]")
    return data

def get_scryfall_bulk(level):
    data = load_with_bar("https://archive.scryfall.com/json/scryfall-all-cards.json")
    return data

def get_scryfall_cards(query):
    return complete_scrython_data(scrython.Search(q=query, unique="prints", include_extras=True, include_multilingual=True))

def get_scryfall_edition(code):
    print(f"Download edition {code}")
    return scrython.foundation.FoundationObject(f"sets/{code}?").scryfallJson
    

def get_scryfall_card(name):
    print(f"Download card {name}")
    return scrython.cards.Named(exact=name).scryfallJson

def get_scryfall_base_card(code, collector_number):
    print(f"Download card {code}/{collector_number}")
    return scrython.cards.collector.Collector(code=code,collector_number=collector_number).scryfallJson

def get_scryfall_printing(code, collector_number, lang):
    print(f"Download card {code}/{collector_number}/{lang}")
    try:
        return scrython.cards.collector.Collector(code=code,collector_number=collector_number, lang=lang).scryfallJson
    except:
        print("Could not find card on scryfall")
        json = scrython.cards.collector.Collector(code=code,collector_number=collector_number).scryfallJson
        json["lang"] = lang
        return json
