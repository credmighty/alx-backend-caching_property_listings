from django.core.cache import cache
from .models import Property

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