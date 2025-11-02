from django.core.cache import cache
from .models import Property
from django_redis import get_redis_connection
import logging

logger = logging.getLogger(__name__)

def get_all_properties():
    #try to get from Redis cache
    properties = cache.get('all_properties')

    if properties is None:
        # Not in cache - fetch in DB
        print("Cache miss: Fetching from database...")
        properties = list(Property.objects.all().values(
            'id', 'title', 'description', 'price', 'location', 'created_at'
        ))

        # Store in Redis for 1hour (3600)
        cache.set('all_properties', properties, 3600)
    else:
        print("Cache hit: Loaded from Redis")

    return properties


def get_redis_cache_metrics():
    """
    Retrieve Redis cache hit/miss metrics and calculate hit ratio.
    Returns a dictionary with metrics.
    """
    try:
        # Connect to the Redis instance used by Django
        redis_conn = get_redis_connection("default")

        # Fetch Redis INFO statistics
        info = redis_conn.info()

        # Extract relevant stats
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)

        # Compute hit ratio safely
        total = hits + misses
        hit_ratio = (hits / total) if total > 0 else 0.0

        metrics = {
            "hits": hits,
            "misses": misses,
            "hit_ratio": round(hit_ratio, 4),
        }

        # Log the metrics for debugging/monitoring
        logger.info(f"Redis Cache Metrics: {metrics}")

        return metrics

    except Exception as e:
        logger.error(f"Error retrieving Redis metrics: {e}")
        return {"error": str(e)}