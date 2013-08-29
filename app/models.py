from content    import ContentObjects, Container
import redis
import settings
import json

class DummyContentCache(object):
    data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value



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
    def load(self, slug):
        obj = content_cache.get(slug)
        if obj:
            print 'was cached!'
            obj = json.loads(obj)
        else:
            print 'uncached, getting from API'
            obj = content_objects.filter(type=Container, slug=slug)
            if len(obj) > 0:
                obj = obj[0]
                content_cache.set(slug, obj.toJSON())
                print 'added to cache'
            else:
                print 'not found'
                obj = None
        return Container(obj)


data_loader = DataLoader()