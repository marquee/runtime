from content        import Container
from data_loader    import content_objects



class ROLES(object):
    STORY       = 'story'
    PUBLICATION = 'publication'
    ISSUE       = 'issue'
    CATEGORY    = 'category'



class MContentModel(object):
    def __init__(self, container):
        self._container = container

    def __getattr__(self, attr_name):
        return getattr(self._container, attr_name)

    @property
    def link(self):
        return '/{0}/'.format(self.slug)



class HasCoverContent(object):
    """
    Private: mixin that adds cover content accessors.
    """
    def cover(self, size=640):
        default = ''

        if not hasattr(self, 'cover_content'):
            return default

        asset = None

        if size == 640:
            asset = self.cover_content['content'].get('640', {})

        elif size == 1280:
            asset = self.cover_content['content'].get('1280', {})

        elif size == 'original':
            asset = self.cover_content['content'].get('original', {})

        if asset:
            return asset.get('url', default)

        return default



class Dotify(object):
    def __init__(self, dict_data):
        self._dict = dict_data
    def __getattr__(self, attr_name):
        return self._dict[attr_name]



class Story(MContentModel, HasCoverContent):

    @property
    def published(self):
        return Dotify(self._container.published_json)



class Publication(MContentModel):
    def stories(self, **kwargs):
        kwargs.update({
                'role': ROLES.STORY,
                'published_date__exists': True,
            })
        stories = content_objects.filter(type=Container, **kwargs).mapOnExecute(Story).sort('-published_date')
        return stories


def modelFromRole(content_obj):
    mapping = {
        ROLES.STORY         : Story,
        ROLES.PUBLICATION   : Publication,
    }
    return mapping[content_obj.role](content_obj)

