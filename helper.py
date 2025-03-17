import json
from dataclasses import asdict
from typing import Any

# TODO: Not to bring in session here, but to take only what is needed.
# TODO: Groups and roles update might be overwriting each other values.
def session_store_obj(session: dict, key: str, obj: Any) -> None:
    """
    Stores a object in the session.

    Args:
        session: The session dictionary.
        key: The key to store the object under.
        obj: The object to store (must be JSON-serializable).
    """
    try:
        data = asdict(obj)
        session[key] = json.dumps(data)
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
        data = json.loads(session.get(key))
        return cls(**data)
    except (json.JSONDecodeError, TypeError):
        return None