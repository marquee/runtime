from content    import ContentObjects, Container
from datetime   import datetime, timedelta
import json
import logging
import redis
import settings



class DummyContentCache(object):
    """
    Internal: a mock cache interface that simulates caching.
    """
    data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        # Cap the data cache to avoid blowing up the memory.
        if len(self.data) > 29:
            self.data = {}
        self.data[key] = value



class RedisPermaCache(object):
    """
    Internal: a wrapper around the redis cache, mapping `hgetall` to get and
    `hmset` to set, for convenience. (This way, the loader is less tied to
    redis and anything that implements `.get` and `.set` in the same way can
    be used.)
    """
    def __init__(self, redis_client):
        """
        redis_client    - a py-redis client that is connected to a redis server
        """
        self._redis = redis_client

    def get(self, key):
        return self._redis.hgetall(key)

    def set(self, key, value):
        self._redis.hmset(key, value)



class CacheLogger(object):
    """
    Internal: a wrapper around the given cache backend, for the purposes of
    logging the hits and misses.
    """
    def __init__(self, cache_backend):
        self._backend = cache_backend

    def get(self, key):
        val = self._backend.get(key)
        if val:
            print 'hit', key
            logging.debug('Cache hit', extra={'key': key})
        else:
            print 'miss', key
            logging.debug('Cache miss', extra={'key': key})
        return val

    def set(self, key, value):
        self._backend.set(key, value)
        logging.debug('Cache set', extra={'key': key})



class DataLoader(object):
    """
    Internal: A class that loads the target data from the cache or the API. If
    the requested object has not been cached, it is retrieved from the content
    API, then cached. The cache is assumed to be a key-value datastore that
    can store hashes (eg, redis).

    Objects are cached with a soft expiry, enforced at the application level,
    so that if the expiration time has passed, the object is re-fetched from
    the content API. However, the object is not cleared from the cache upon
    expiry, in case the content API is unreachable. The objects are recorded
    using the time stored, so the staleness can be adjusted even after the
    object was cached.
    """
    def __init__(self, cache_backend=None, content_backend=None, stale_after=None):
        if not stale_after:
            stale_after = timedelta(minutes=10)
        if cache_backend:
            cache_backend = CacheLogger(cache_backend)

        self._stale_after   = stale_after
        self._content       = content_backend
        self._cache         = cache_backend

    def load(self, stale_after=None, **kwargs):
        target_object = None

        if not stale_after:
            stale_after = self._stale_after

        if self._cache:
            cached_object = self._cache.get(kwargs_to_key(kwargs))
            # cached form:
            # {
            #     'stored_at' : '1377816338',
            #     'object'    : '{ "slug": "some-title", "title": "Some Title" }',
            # }

            if cached_object and 'stored_at' in cached_object:
                # Object was cached, so check if it has expired yet.
                object_stored_at = datetime.fromtimestamp(int(cached_object['stored_at']))

                if datetime.utcnow() - object_stored_at > stale_after:
                    # It has expired, so try getting it from the API instead.
                    target_object = self._load_from_api(**kwargs)
                else:
                    # Convert the cached JSON to a Container.
                    target_object = Container(json.loads(cached_object['object']))

        if not target_object:
            # Object was not cached (or no cache used), so load from the API.
            target_object = self._load_from_api(**kwargs)

        return target_object

    def _load_from_api(self, **kwargs):
        """
        Internal: load the target object from the Content API using the
        specified slug. If the object is found and a cache_backend was
        specified, the object's JSON str representation is cached. 

        If more than one object matches, None is returned and the error is
        logged.

        Returns a Container, or None.
        """
        obj = self._content.filter(type=Container, **kwargs)
        if len(obj) == 1:
            obj = obj[0]
            logging.debug('Object found', extra=kwargs)
            if self._cache:
                self._cache.set(kwargs_to_key(kwargs), {
                        'stored_at' : datetime.utcnow().strftime('%s'),
                        'object'    : obj.toJSON(),
                    })
        else:
            if obj:
                logging.warning('Got multiple results for a slug', extra=kwargs)
            else:
                logging.debug('Object not found', extra=kwargs)
            obj = None
        return obj



def kwargs_to_key(kwargs):
    if 'short_name' in kwargs:
        return "short_name:{short_name}".format(**kwargs)
    return "slug:{slug}".format(**kwargs)



if settings.REDIS_URL:
    content_cache = RedisPermaCache(redis.from_url(settings.REDIS_URL))
else:
    content_cache = DummyContentCache()

# Single-user/single-app application, so we can just have a single API instance.
content_objects = ContentObjects(
        settings.CONTENT_API_TOKEN,
        api_root = settings.CONTENT_API_ROOT,
    )

data_loader = DataLoader(
        cache_backend   = content_cache,
        content_backend = content_objects,
        stale_after     = timedelta(minutes=settings.CACHE_SOFT_EXPIRY),
    )
