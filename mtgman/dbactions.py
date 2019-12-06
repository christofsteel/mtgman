from .model import Card
from .parser import parser




#def get_scryfall_cards(query):
#    return complete_scrython_data(scrython.Search(q=query, unique="prints", include_extras=True, include_multilingual=True))

#def get_scryfall_sets():
#    return complete_scrython_data(scrython.foundation.FoundationObject("sets?"))


#def find_by_scryfall_id(all_cards, id):
#    card = all_cards.get(id)
#    if card is not None:
#        return card
#    print(f"Failed to find card: {id}, try online.")
#    return scrython.cards.Id(id = id).scryfallJson
#
#def find_first_by_name(all_cards, name):
#    for e in all_cards.values():
#        if e.get("name") == name:
#            return e
#    raise RuntimeError(f"did not find card: {id}")
#
#def find_all_by_name(all_cards, name):
#    l = []
#    for e in all_cards.values():
#        if e.get("name") == name:
#            l.append(e)
#    return l


def dbquery(query, session):
    parsed_query = parser.parse(query)
    for res in session.query(Card).filter(parsed_query.dbfilter()).all():
        print(f"{res.name}, {res.mana_cost}, {res.type_line}")
