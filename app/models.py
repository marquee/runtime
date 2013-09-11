from content        import Container
from .data_loader   import content_objects



class ROLES(object):
    STORY       = 'story'
    PUBLICATION = 'publication'
    ISSUE       = 'issue'
    CATEGORY    = 'category'



class MContentModel(object):
    """
    Internal: A base class that wraps the Container content object, providing
    accessors directly to the Container instance as well as some helper
    methods.
    """
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

    def cover(self, size='640'):
        """
        Public: return the URL for the specified image size, or '' if the
        object doesn't have a cover_content image of that size.

        size - (optional: '640') The int or str size to select.

        Returns the string URL of the image.
        """

        default = ''

        if not hasattr(self, 'cover_content'):
            return default

        asset = None

        size = str(size)

        if size == '640':
            asset = self.cover_content['content'].get('640', {})

        elif size == '1280':
            asset = self.cover_content['content'].get('1280', {})

        elif size == 'original':
            asset = self.cover_content['content'].get('original', {})

        if asset:
            return asset.get('url', default)

        return default



class Issue(MContentModel, HasCoverContent):
    """
    Public: A model that corresponds to a Container with role='issue'.
    """

    def stories(self, *args, **kwargs):
        """
        Public: returns all stories that belong to the Issue

        Returns an APIQuery containing instances of Story objects for
        every story in an issue.
        """

        stories = content_objects.filter(
            issue_content=self.id
        ).mapOnExecute(Story)

        return stories



class Story(MContentModel, HasCoverContent):
    """
    Public: A model that corresponds to a Container with role='story'.
    """

    @property
    def published(self):
        """
        Public: map the published data to .published.

        Right now, uses the `_include_published` flag on the query. However,
        it may change to be a query like `?_as_of=@published_date`, so this
        abstraction will keep the template API consistent.

        Returns a Story copy of the story instance in its published state, or
        None if the instance is not published.
        """
        if self._container._published_json:
            return Story(Container(self._container._published_json[0]))
        return None



class Publication(MContentModel):
    """
    Public: A model that corresponds to a Container with `role='publication'`.
    """

    def issues(self, *args, **kwargs):
        """
        Public: load the Issues that belong to the Publication instance from
        the API, filtered by the specified arguments.

        args    - (optional) A single dict to use for the query, allowing for
                    query keys that cannot be used as keywoard arguments.

        kwargs  - (optional) Keyword arguments that are added to the query,
                    superseding any query specified as a positional argument.

        Note: the query is updated to filter by role and to only include
        published stories.

        Returns an (iterable, lazy) APIQuery of Story objects.
        """
        query = {}

        if len(args) > 0:
            query.update(args[0])

        query.update(kwargs)
        query.update({
            'role'                      : ROLES.ISSUE,
        })

        # Construct the APIQuery and return the results as Issue objects.
        issues = content_objects.filter(
            type=Container, **query
        ).mapOnExecute(Issue)

        return issues


    def stories(self, *args, **kwargs):
        """
        Public: load the Stories that belong to the Publication instance from
        the API, filtered by the specified arguments.

        args    - (optional) A single dict to use for the query, allowing for
                    query keys that cannot be used as keyword arguments.
        kwargs  - (optional) Keyword arguments that are added to the query,
                    superseding any query specified as a positional argument.

        Note: the query is updated to filter by role and to only include
        published stories.

        Returns an (iterable, lazy) APIQuery of Story objects.
        """
        query = {}

        if len(args) > 0:
            query.update(args[0])

        query.update(kwargs)
        query.update({
                'role'                      : ROLES.STORY,
                'published_date__exists'    : True,
            })

        # Construct the APIQuery and return the results as Story objects.
        stories = content_objects.filter(
                type=Container, **query
            ).mapOnExecute(Story).sort('-published_date')

        return stories



def modelFromRole(content_obj):
    """
    Public: convert a Content object to the appropriate Marquee model.

    content_obj - the Container to wrap in the model.

    Returns an Issue, Story, or Publication instance.
    """
    mapping = {
        ROLES.ISSUE         : Issue,
        ROLES.STORY         : Story,
        ROLES.PUBLICATION   : Publication,
    }
    return mapping[content_obj.role](content_obj)
