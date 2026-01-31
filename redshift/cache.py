"""
Simple TTL (Time-To-Live) cache for schema metadata.
Provides thread-safe caching with expiration support.
"""
import time
import threading
from typing import Any, Optional


class TTLCache:
    """
    Thread-safe cache with TTL (Time-To-Live) support.
    Entries expire after a specified number of seconds.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize the TTL cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 300s / 5 minutes)
        """
        self.default_ttl = default_ttl
        self._cache = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache if it exists and hasn't expired.

        Args:
            key: The cache key

        Returns:
            The cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            # Check if entry has expired
            if time.time() > entry['expires_at']:
                # Remove expired entry
                del self._cache[key]
                return None

            return entry['value']

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set a value in the cache with optional TTL.

        Args:
            key: The cache key
            value: The value to cache
            ttl_seconds: Time-to-live in seconds. If None, uses default_ttl
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }

    def invalidate(self, key: str) -> None:
        """
        Remove a specific key from the cache.

        Args:
            key: The cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> None:
        """Remove all expired entries from the cache."""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry['expires_at']
            ]
            for key in expired_keys:
                del self._cache[key]

    def __len__(self) -> int:
        """Return the number of valid (non-expired) entries in the cache."""
        with self._lock:
            current_time = time.time()
            return sum(
                1 for entry in self._cache.values()
                if current_time <= entry['expires_at']
            )

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache and hasn't expired."""
        return self.get(key) is not None
