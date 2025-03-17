from typing import Any
import pickle
from redshift.database import Redshift
from redshift.user import RedshiftUser
from redshift.role import RedshiftRole
from redshift.group import RedshiftGroup


__all__ = [
    'sess_store_obj', 'sess_get_obj', 'get_rs', 'set_rs',
    'get_user', 'set_user', 'get_role', 'set_role',
    'get_group', 'set_group'
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

def set_role(session, role: RedshiftRole):
    sess_store_obj(session, 'rsrole', role)

def get_role(session) -> RedshiftRole:
    return sess_get_obj(session, 'rsrole')

def set_group(session, group: RedshiftGroup):
    sess_store_obj(session, 'rsgroup', group)

def get_group(session) -> RedshiftGroup:
    return sess_get_obj(session, 'rsgroup')
