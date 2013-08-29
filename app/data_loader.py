from content    import ContentObjects, Container

from datetime import datetime, timedelta
import redis
import settings
import json


class DummyContentCache(object):
    """
    Private: a mock cache interface that simulates caching.
    """
    data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        if len(self.data) > 29:
            self.data = {}
        self.data[key] = value





import logging


class RedisPermaCache(object):
    """
    Private: a wrapper around the redis cache, mapping hgetall to get and
             hmset to set.
    """
    def __init__(self, redis_client):
        self._redis = redis_client

    def get(self, key):
        return self._redis.hgetall(key)

    def set(self, key, value):
        self._redis.hmset(key, value)


class CacheLogger(object):
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
    Private: A class that loads the target data from the cache or the API. If
             the requested object has not been cached, it is retrieved from
             the content API, then cached. The cache is assumed to be a
             key-value datastore that can store hashes (redis).

             Objects are cached with a soft expiry, enforced at the
             application level, so that if the expiration time has passed, the
             object is re-fetched from the content API. However, the object is
             not expiry cleared from the cache upon expiry, in case the
             content API is unreachable.
    """
    def __init__(self, cache_backend=None, content_backend=None, stale_after=None):
        if not stale_after:
            stale_after = timedelta(minutes=10)
        if cache_backend:
            cache_backend = CacheLogger(cache_backend)

        self._stale_after   = stale_after
        self._content       = content_backend
        self._cache         = cache_backend

    def load(self, slug):
        target_object = None

        if self._cache:
            cached_object = self._cache.get(slug)
            print cached_object
            # cached form:
            # {
            #     'stored_at' : '1377816338',
            #     'object'    : '{ "slug": "some-title", "title": "Some Title" }',
            # }

            if cached_object and 'stored_at' in cached_object:
                # Object was cached, so check if it has expired yet.
                object_stored_at = datetime.fromtimestamp(int(cached_object['stored_at']))

                if datetime.utcnow() - object_stored_at > self._stale_after:
                    # It has expired, so try getting it from the API instead.
                    target_object = self._load_from_api(slug)
                else:
                    # Convert the cached JSON to a Container.
                    target_object = Container(json.loads(cached_object['object']))

        if not target_object:
            # Object was not cached (or no cache used), so load from the API.
            target_object = self._load_from_api(slug)

        return target_object

    def _load_from_api(self, slug):
        """
        Private: load the target object from the Content API using the
                 specified slug. If the object is found and a cache_backend
                 was specified, the object's JSON representation is cached. 

        Returns a Container, or None.
        """
        obj = self._content.filter(type=Container, slug=slug)
        if len(obj) == 1:
            obj = obj[0]
            logging.debug('Object found', extra={'slug': slug})
            if self._cache:
                self._cache.set(slug, {
                        'stored_at': datetime.utcnow().strftime('%s'),
                        'object': obj.toJSON(),
                    })
        else:
            if obj:
                logging.warning('Got multiple results for a slug', extra={'slug': slug})
            else:
                logging.debug('Object not found', extra={'slug': slug})
            obj = None
        return obj






        # obj = self._cache.get(slug)
        # if obj:
        #     print 'was cached!'
        #     obj = json.loads(obj)
        # else:
        #     print 'uncached, getting from API'
        #     obj = content_objects.filter(type=Container, slug=slug)
        #     if len(obj) > 0:
        #         obj = obj[0]
        #         content_cache.set(slug, obj.toJSON())
        #         print 'added to cache'
        #     else:
        #         print 'not found'
        #         obj = None
        # return Container(obj)



if settings.REDIS_URL:
    content_cache = RedisPermaCache(redis.from_url(settings.REDIS_URL))
else:
    content_cache = DummyContentCache()

# Single-user/single-app application, so we can just have a single API instance.
content_objects = ContentObjects(
        settings.CONTENT_API_TOKEN,
        api_root=settings.CONTENT_API_ROOT
    )

data_loader = DataLoader(
        cache_backend   = content_cache,
        content_backend = content_objects,
        stale_after     = timedelta(minutes=settings.CACHE_SOFT_EXPIRY),
    )
