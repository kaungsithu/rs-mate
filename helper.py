import json
from dataclasses import asdict
from typing import Any
import pickle
from redshift import Redshift
from user import RedshiftUser


__all__ = [
    'sess_store_obj', 'sess_get_obj', 'get_rs', 'set_rs',
    'get_user', 'set_user'
    ]

def sess_store_obj(session: dict, key: str, obj:Any):
    'store pickled object in session'
    try:
        session[key] = pickle.dumps(obj).hex()
    except Exception as e:
        print(f'Error pickling {key}: {e}')

def sess_get_obj(session: dict, key: str):
    'get pickled object from session'
    try:
        return pickle.loads(bytes.fromhex(session.get(key)))
    except Exception as e:
        print(f'Error unpickling {key}: {e}')
        return None

def set_rs(session: dict, rs: Redshift):
    sess_store_obj(session, 'redshift', rs)

def get_rs(session: dict) -> Redshift:
    return sess_get_obj(session, 'redshift')

def set_user(session: dict, user: RedshiftUser):
    sess_store_obj(session, 'rsuser', user)

def get_user(session: dict) -> RedshiftUser:
    return sess_get_obj(session, 'rsuser')