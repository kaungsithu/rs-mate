import json
from dataclasses import asdict
from typing import Any

def session_store_obj(session: dict, key: str, obj: Any) -> None:
    """
    Stores a object in the session.

    Args:
        session: The session dictionary.
        key: The key to store the object under.
        obj: The object to store (must be JSON-serializable).
    """
    try:
        session[key] = json.dumps(asdict(obj))
    except TypeError:
        print(f"Error: Object with key '{key}' is not JSON serializable.")
        # Optionally, you might want to raise the exception or handle it differently.

def session_get_obj(session: dict, key: str, cls: Any) -> Any:
    """
    Retrieves a JSON-serializable object from the session.

    Args:
        session: The session dictionary.
        key: The key to retrieve the object from.
        default: The default value to return if the key is not found or the object is not valid JSON.

    Returns:
        The retrieved object, or the default value.
    """
    try:
        return cls(**json.loads(session.get(key)))
    except (json.JSONDecodeError, TypeError):
        return None