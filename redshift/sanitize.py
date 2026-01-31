"""
SQL sanitization utilities for preventing SQL injection in DDL/DCL statements.

Since Redshift DDL/DCL statements do not support parameterized identifiers,
we use strict allowlist validation and literal escaping instead.
"""

import re
from typing import Tuple


# Strict regex for valid SQL identifiers: [a-zA-Z_][a-zA-Z0-9_]{0,126}
VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,126}$')


def validate_identifier(name: str) -> str:
    """
    Validate a SQL identifier (username, role, group, schema, table, etc.)
    against a strict allowlist regex.

    Args:
        name: The identifier to validate

    Returns:
        The validated identifier (unchanged if valid)

    Raises:
        ValueError: If the identifier is invalid
    """
    if not isinstance(name, str):
        raise ValueError(f"Identifier must be a string, got {type(name).__name__}")

    if not name:
        raise ValueError("Identifier cannot be empty")

    if not VALID_IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid identifier '{name}': must start with a letter or underscore, "
            f"contain only alphanumerics and underscores, and be at most 127 characters"
        )

    return name


def escape_literal(value: str) -> str:
    """
    Escape a string literal for SQL by doubling single quotes and wrapping in quotes.

    This prevents SQL injection in string literals.

    Args:
        value: The string value to escape

    Returns:
        The escaped and quoted string literal (e.g., 'value with ''quotes''')

    Raises:
        ValueError: If the value contains null bytes
    """
    if not isinstance(value, str):
        raise ValueError(f"Literal must be a string, got {type(value).__name__}")

    if '\0' in value:
        raise ValueError("String literals cannot contain null bytes")

    # Double single quotes and wrap in single quotes
    escaped = value.replace("'", "''")
    return f"'{escaped}'"
