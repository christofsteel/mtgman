from datetime import datetime
from uuid import UUID

def is_simpl_digit(i):
    i in "0123456789"

def create_dict( e
               , fields = [] 
               , fields_int = []
               , fields_date = []
               , fields_uuid = []
               , lists = []
               , lists_uuid = []
               , renames = {}
               , renames_uuid = {}
               , objects = {}
               , custom = {}
               , ignore = []):
    dict_fields = {f:e.get(f) for f in fields}
    dict_fields_int = {f:(int("".join(filter(is_simpl_digit,e.get(f)))) if "".join(filter(is_simpl_digit,e.get(f))).isdigit() else 0) for f in fields_int if e.get(f) is not None}
    dict_fields_date = {f:(datetime.strptime(e.get(f), "%Y-%m-%d") if e.get(f) is not None else None) for f in fields_date}
    dict_fields_uuid = {f:(UUID(e.get(f)) if e.get(f) is not None else None) for f in fields_uuid}
    dict_lists = {f:(e.get(f) if e.get(f) is not None else []) for f in lists}
    dict_lists_uuid = {f:[UUID(u) for u in e.get(f)] if e.get(f) is not None else [] for f in lists_uuid}
    dict_renames = {v:e.get(k) for k,v in renames.items()}
    dict_renames_uuid = {v:(UUID(e.get(k)) if e.get(k) is not None else None) for k, v in renames_uuid.items()}
    dict_objects = {vv[0]:vv[1](e.get(f).get(k)) for f,v in objects.items() for k,vv in v.items() if e.get(f) is not None}

    dict_all = { **dict_fields, **dict_fields_int, **dict_fields_date
               , **dict_fields_uuid, **dict_lists, **dict_lists_uuid
               , **dict_renames, **dict_renames_uuid, **dict_objects, **custom}
    return dict_all
