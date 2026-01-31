"""
Middleware for session security: expiration and CSRF protection.
"""

import time
import secrets
import os
from typing import Optional


# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT_SECONDS = 30 * 60

# CSRF token length
CSRF_TOKEN_LENGTH = 32


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def init_session(session: dict) -> None:
    """
    Initialize session with timestamp and CSRF token.

    Args:
        session: The session dictionary
    """
    session['_session_created_at'] = time.time()
    session['_csrf_token'] = generate_csrf_token()


def check_session_expiry(session: dict) -> bool:
    """
    Check if session has expired due to inactivity.

    Args:
        session: The session dictionary

    Returns:
        True if session is still valid, False if expired
    """
    created_at = session.get('_session_created_at')

    if created_at is None:
        # No timestamp means session needs to be re-initialized
        return False

    elapsed = time.time() - created_at

    if elapsed > SESSION_TIMEOUT_SECONDS:
        return False

    return True


def get_csrf_token(session: dict) -> str:
    """
    Get or create CSRF token for the session.

    Args:
        session: The session dictionary

    Returns:
        The CSRF token
    """
    token = session.get('_csrf_token')

    if not token:
        token = generate_csrf_token()
        session['_csrf_token'] = token

    return token


def validate_csrf_token(session: dict, token: str) -> bool:
    """
    Validate CSRF token.

    Args:
        session: The session dictionary
        token: The token to validate

    Returns:
        True if token is valid, False otherwise
    """
    expected_token = session.get('_csrf_token')

    if not expected_token:
        return False

    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(expected_token, token)
