from content    import ContentObjects
import redis
import settings

class DummyContentCache(object):
    data = {}

    def get(self, key):
        return data.get(key)

    def set(self, key, value):
        data[key] = value



if settings.REDIS_URL:
    content_cache = redis.from_url(settings.REDIS_URL)
else:
    content_cache = DummyContentCache()

# Single-user/single-app application, so we can just have a single API instance.
content_objects = ContentObjects(
        settings.CONTENT_API_TOKEN,
        api_root=settings.CONTENT_API_ROOT
    )


class DataLoader(object):
    def load(self, **kwargs):
        """
        get object from redis
        if not object
            get object from content api
            if object
                store object in redis
        """
        return kwargs


data_loader = DataLoader()