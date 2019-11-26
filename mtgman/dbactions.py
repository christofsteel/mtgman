import scrython
from tqdm import tqdm
import requests
from io import BytesIO
import json

def complete_scrython_data(scrython_object):
    data = scrython_object.data()
    while scrython_object.has_more():
        data.next_page()
        data += scrython_object.data()
    return data

def get_scryfall_cards():
    url = scrython.BulkData().bulk_permalink_uri(0)
    response = requests.get(url)
    total_size = int(response.headers.get("content-length", 0))
    chunk_size = 1024
    buf = BytesIO()
    print(f"total size: {total_size}")
    bar = tqdm(total = total_size, unit='B', unit_scale=True, desc="Ihre Werbung")
    for chunk in response.iter_content(chunk_size=chunk_size):
        buf.write(chunk)
        bar.update(1024)
    buf.seek(0)
    cards = json.load(buf)
    return cards

def get_scryfall_sets():
    return complete_scrython_data(scrython.sets.Sets())