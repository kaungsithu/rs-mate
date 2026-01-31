"""
Tests for the TTLCache class in redshift/cache.py
"""
import pytest
import time
import threading
from redshift.cache import TTLCache


class TestTTLCache:
    """Test the TTLCache implementation."""

    def test_cache_set_and_get(self):
        """Test basic set and get operations."""
        cache = TTLCache(default_ttl=10)

        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

    def test_cache_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        cache = TTLCache()

        assert cache.get('nonexistent') is None

    def test_cache_expiration(self):
        """Test that entries expire after TTL."""
        cache = TTLCache(default_ttl=1)

        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('key1') is None

    def test_cache_custom_ttl(self):
        """Test setting a custom TTL for an entry."""
        cache = TTLCache(default_ttl=10)

        cache.set('key1', 'value1', ttl_seconds=1)
        assert cache.get('key1') == 'value1'

        time.sleep(1.1)
        assert cache.get('key1') is None

    def test_cache_invalidate(self):
        """Test invalidating a specific cache entry."""
        cache = TTLCache()

        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

        cache.invalidate('key1')
        assert cache.get('key1') is None

    def test_cache_clear(self):
        """Test clearing all cache entries."""
        cache = TTLCache()

        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')

        cache.clear()
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None

    def test_cache_contains(self):
        """Test the __contains__ method."""
        cache = TTLCache(default_ttl=10)

        cache.set('key1', 'value1')
        assert 'key1' in cache
        assert 'nonexistent' not in cache

    def test_cache_len(self):
        """Test the __len__ method."""
        cache = TTLCache(default_ttl=10)

        assert len(cache) == 0

        cache.set('key1', 'value1')
        assert len(cache) == 1

        cache.set('key2', 'value2')
        assert len(cache) == 2

        cache.invalidate('key1')
        assert len(cache) == 1

    def test_cache_overwrite_value(self):
        """Test overwriting an existing cache entry."""
        cache = TTLCache()

        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

        cache.set('key1', 'value2')
        assert cache.get('key1') == 'value2'

    def test_cache_cleanup_expired(self):
        """Test the cleanup_expired method."""
        cache = TTLCache(default_ttl=1)

        cache.set('key1', 'value1')
        cache.set('key2', 'value2', ttl_seconds=10)

        time.sleep(1.1)
        cache.cleanup_expired()

        # key1 should be removed, key2 should remain
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'

    def test_cache_thread_safety(self):
        """Test that concurrent access to the cache is thread-safe."""
        cache = TTLCache()
        errors = []

        def writer():
            try:
                for i in range(100):
                    cache.set(f'key_{i}', f'value_{i}')
            except Exception as e:
                errors.append(str(e))

        def reader():
            try:
                for i in range(100):
                    cache.get(f'key_{i}')
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads for reading and writing
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=writer))
            threads.append(threading.Thread(target=reader))

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)

        # Check for errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

    def test_cache_with_different_data_types(self):
        """Test caching different data types."""
        cache = TTLCache()

        # String
        cache.set('string_key', 'value')
        assert cache.get('string_key') == 'value'

        # Integer
        cache.set('int_key', 42)
        assert cache.get('int_key') == 42

        # List
        cache.set('list_key', [1, 2, 3])
        assert cache.get('list_key') == [1, 2, 3]

        # Dictionary
        cache.set('dict_key', {'a': 1, 'b': 2})
        assert cache.get('dict_key') == {'a': 1, 'b': 2}

        # None
        cache.set('none_key', None)
        assert cache.get('none_key') is None

    def test_cache_empty_operations(self):
        """Test operations on an empty cache."""
        cache = TTLCache()

        # Invalidate on empty cache should not raise error
        cache.invalidate('nonexistent')

        # Cleanup on empty cache should not raise error
        cache.cleanup_expired()

        # Clear on empty cache should not raise error
        cache.clear()

        # Length of empty cache should be 0
        assert len(cache) == 0
