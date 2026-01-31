from typing import Any, Optional, Type
import json
from dataclasses import asdict, is_dataclass
from redshift.database import Redshift
from redshift.user import RedshiftUser
from redshift.role import RedshiftRole
from redshift.group import RedshiftGroup


__all__ = [
    'sess_store_obj', 'sess_get_obj', 'get_rs', 'set_rs',
    'get_user', 'set_user', 'get_role', 'set_role',
    'get_group', 'set_group'
]


def sess_store_obj(session: dict, key: str, obj: Any):
    """Store a JSON-serializable object in session."""
    try:
        if is_dataclass(obj) and not isinstance(obj, type):
            # Convert dataclass to dictionary
            data = asdict(obj)
        else:
            data = obj

        session[key] = json.dumps(data)
    except Exception as e:
        print(f'Error serializing {key}: {e}')


def sess_get_obj(session: dict, key: str, cls: Optional[Type] = None) -> Any:
    """
    Retrieve a JSON-serialized object from session.

    Args:
        session: The session dictionary
        key: The session key
        cls: Optional dataclass type to deserialize into. If None, returns dict.

    Returns:
        The deserialized object or None if not found/error
    """
    try:
        json_str = session.get(key)
        if not json_str:
            return None

        data = json.loads(json_str)

        if cls is None:
            return data

        # Deserialize to the specified dataclass
        if cls == RedshiftUser:
            return RedshiftUser(**data)
        elif cls == RedshiftRole:
            return RedshiftRole(**data)
        elif cls == RedshiftGroup:
            return RedshiftGroup(**data)
        elif is_dataclass(cls):
            return cls(**data)
        else:
            return data
    except Exception as e:
        print(f'Error deserializing {key}: {e}')
        return None


def set_rs(session: dict, rs: Redshift):
    """Store Redshift connection in session (stores connection params, not the connection object)."""
    try:
        # Store only the connection parameters, not the connection object
        conn_data = {
            'host': rs.host,
            'port': rs.port,
            'database': rs.database,
            'user': rs.user,
            'name': rs.name  # Database name
        }
        session['redshift'] = json.dumps(conn_data)
    except Exception as e:
        print(f'Error storing Redshift connection: {e}')


def get_rs(session: dict) -> Optional[Redshift]:
    """Retrieve Redshift connection info from session."""
    try:
        json_str = session.get('redshift')
        if not json_str:
            return None

        data = json.loads(json_str)
        # Note: This returns the connection parameters, not an active connection
        # The actual connection should be established separately
        return Redshift(
            host=data.get('host'),
            port=data.get('port', 5439),
            database=data.get('database'),
            user=data.get('user')
        )
    except Exception as e:
        print(f'Error retrieving Redshift connection: {e}')
        return None


def set_user(session: dict, user: RedshiftUser):
    """Store RedshiftUser in session."""
    sess_store_obj(session, 'rsuser', user)


def get_user(session: dict) -> Optional[RedshiftUser]:
    """Retrieve RedshiftUser from session."""
    return sess_get_obj(session, 'rsuser', RedshiftUser)


def set_role(session: dict, role: RedshiftRole):
    """Store RedshiftRole in session."""
    sess_store_obj(session, 'rsrole', role)


def get_role(session: dict) -> Optional[RedshiftRole]:
    """Retrieve RedshiftRole from session."""
    return sess_get_obj(session, 'rsrole', RedshiftRole)


def set_group(session: dict, group: RedshiftGroup):
    """Store RedshiftGroup in session."""
    sess_store_obj(session, 'rsgroup', group)


def get_group(session: dict) -> Optional[RedshiftGroup]:
    """Retrieve RedshiftGroup from session."""
    return sess_get_obj(session, 'rsgroup', RedshiftGroup)
