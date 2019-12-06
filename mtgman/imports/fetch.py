from tqdm import tqdm
from sqlalchemy.exc import IntegrityError

from .scryfall import get_scryfall_cards
from .printing import add_printing

def import_cards(query, session):
    cards = get_scryfall_cards(query)
    for card in tqdm(cards):
        try:
            add_printing(card, session)
            session.commit()
        except IntegrityError:
            session.rollback()
    
