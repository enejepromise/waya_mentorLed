# waya_backend/cache_utils.py

from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_or_set_cache(key: str, timeout: int, compute_func):
    """
    Try to get the value from the cache. If not available, compute it,
    cache it, and return it.

    Args:
        key (str): The cache key to use.
        timeout (int): The cache timeout in seconds.
        compute_func (Callable): A function that returns the data to be cached.

    Returns:
        Any: The cached or computed data.
    """
    try:
        value = cache.get(key)
        if value is not None:
            logger.debug(f"[CACHE-HIT] Key: {key}")
            return value
        
        logger.debug(f"[CACHE-MISS] Key: {key}. Generating and setting new value.")
        value = compute_func()
        cache.set(key, value, timeout)
        return value

    except Exception as e:
        logger.error(f"[CACHE-ERROR] Key: {key} — {str(e)}")
        # Fallback: return freshly computed value in case of cache failure
        return compute_func()


def invalidate_cache(key: str):
    """
    Remove a key from the cache if it exists.

    Args:
        key (str): The cache key to delete.
    """
    try:
        cache.delete(key)
        logger.debug(f"[CACHE-DELETE] Key: {key}")
    except Exception as e:
        logger.error(f"[CACHE-DELETE-ERROR] Key: {key} — {str(e)}")
