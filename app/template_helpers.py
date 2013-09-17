from app        import app
from cgi        import escape
from composer   import renderBlock
from content    import Text
from content.models     import instanceFromRaw
from jinja2     import evalcontextfilter, Markup

from .models    import modelFromRole

import settings



# Add various items to the template globals
app.jinja_env.globals.update(ENVIRONMENT=settings.ENVIRONMENT)
app.jinja_env.globals.update(DEBUG=settings.DEBUG)



def static_url(path):
    """
    Public: helper for including static media assets in templates.

    Example

        {{ static_url('images/file.jpg') }}

    path - a String path to the asset, relative to the root of the static folder

    Returns the absolute URL to the asset.
    """
    return u'{0}{1}'.format(settings.STATIC_URL, path)
app.jinja_env.globals.update(static_url=static_url)



def media_url(path):
    """
    Public: helper for including user-uploaded media in templates.

    Example

        {{ media_url('images/file.jpg') }}

    path - a String path to the asset, relative to the root of the media folder

    Returns the absolute URL to the asset.
    """
    return u'{0}{1}'.format(settings.MEDIA_URL, path)
app.jinja_env.globals.update(media_url=media_url)



def to_item_size(count, floor=1, ceiling=5):
    """
    Public: filter that converts a count of items to the appropriate size for
    [Formwork](https://github.com/droptype/formwork)'s `.item-` variants.
    
    count       - the int count of items
    floor       - (optional: 1) the lowest number to use (for ensuring a
                    maximum size)
    ceiling     - (optional: 5) the highest number to use (for ensuring a
                    minimum size)
    Examples

        {% set stories=publication.stories().limit(4) %}
        {% for story in stories %}
            <div class="item-{{ stories|to_item_size }}">
                ...
            </div>
        {% endfor %}

        {% set stories=publication.stories().limit(8) %}
        {% for story in stories %}
            <div class="item-{{ stories|to_item_size(floor=2, ceiling=4) }}">
                ...
            </div>
        {% endfor %}

    Returns the str size name.
    """

    if count < floor:
        count = floor
    elif count > ceiling:
        count = ceiling

    size_map = {
        1: 'full',
        2: 'half',
        3: 'third',
        4: 'fourth',
        5: 'fifth',
    }
    return size_map.get(count, 'full')
app.jinja_env.filters['to_item_size'] = to_item_size



@evalcontextfilter
def render_block(eval_ctx, block):
    """
    Public: a filter that renders the given block.

    block - the Block to render

    Returns the str markup for the block.
    """
    result = renderBlock(block)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
app.jinja_env.filters['render_block'] = render_block



@evalcontextfilter
def content_preview(eval_ctx, story, char_limit=400):
    """
    Public: a filter that generates a content preview for a Story. Uses the
            description of the Story, if it has one, or the text content.

    story         - the Story to preview
    char_limit    - (optional:400) the int number of characters to show

    Examples

        {{ story|content_preview }}

        {{ story|content_preview(char_limit=200) }}

    Returns a str of HTML up to `char_limit` content characters long (count
    doesn't include markup).
    """
    # Default to an empty string since this is for a template.
    content_preview = u''
    generate_preview = True

    if hasattr(story, 'description'):
        if story.description == '' or story.description is None:
            generate_preview = True
        else:
            generate_preview = False
            content_preview = story.description[:char_limit]
            if len(story.description) > char_limit:
                content_preview += '&hellip;'

    if generate_preview:
        content_preview_text_length = 0

        for block in story.content:

            # Only include Text blocks that aren't pre-formatted.
            if block and block.type == Text.type and block.role != 'pre':
                content = block.content.lstrip().rstrip()
                if content:

                    # If this iteration of content will put the total over the
                    # limit, truncate it.
                    if content_preview_text_length + len(content) > char_limit:
                        content = content[:char_limit - content_preview_text_length]

                    # Keep track of the preview length.
                    content_preview_text_length += len(content)

                    # Escape after, so character count doesn't include markup.
                    content = escape(content)

                    # Add an ellipsis to the content to append if over the limit.
                    if content_preview_text_length >= char_limit:
                        content += '&hellip;'

                    # Wrap the iteration's snippet in a tag that indicates the
                    # role, to allow for styling.
                    content_preview += u" <span data-role='{0}'>{1}</span>".format(block.role, content)
                    if content_preview_text_length >= char_limit:
                        break

    if eval_ctx.autoescape:
        content_preview = Markup(content_preview)

    return content_preview
app.jinja_env.filters['content_preview'] = content_preview



@evalcontextfilter
def render_cover(eval_ctx, obj):
    """
    Public: a filter that renders the cover content for a given content object
    The type of cover is determined by the `cover_content` property, and the
    correct template is loaded from the `templates/includes/` folder.

    eval_ctx - the template EvaluationContext (provided automatically)
    obj      - the ContentObject that has cover content (Story, Issue, or
                 Category)

    Examples

        {{ story|render_cover }}

    Returns a unicode HTML fragment, or empty string.
    """
    from content import Image, Embed

    cover_type = None
    context = {}
    result = u''

    if obj and hasattr(obj, 'cover_content'):
        if isinstance(obj.cover_content, list):
            cover_type = 'gallery'
            context['cover_urls'] = [{
                '1280': img.get('content', {}).get('1280', {}).get('url'),
                '640': img.get('content', {}).get('640', {}).get('url'),
            } for img in obj.cover_content]
        else:
            # Only render the cover if it actually has content set.
            if getattr(obj.cover_content, 'type', None) == Image.type and obj.cover_content.get('content'):
                cover_type = 'image'
                context['cover_urls'] = {
                    '1280': obj.cover_content.get('content').get('1280', {}).get('url'),
                    '640': obj.cover_content.get('content').get('640', {}).get('url'),
                }
            elif hasattr(obj.cover_content, 'get'):
                context['cover_urls'] = {}
                context['embed_url'] = ''
                if obj.cover_content.get('embed'):
                    context['embed_url'] = obj.cover_content['embed'].get('content', '')
                if obj.cover_content.get('image'):
                    context['cover_urls'] = {
                        '1280': obj.cover_content['image'].get('content').get('1280', {}).get('url'),
                        '640': obj.cover_content['image'].get('content').get('640', {}).get('url'),
                    }
                if len(context) > 0:
                    cover_type = 'embed'

        if cover_type:
            template = app.jinja_env.get_template('includes/cover_{0}.html'.format(cover_type))
            result = template.render(context)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
app.jinja_env.filters['render_cover'] = render_cover



@evalcontextfilter
def asModel(eval_ctx, obj_dict):
    """
    Public: a filter that converts a dict to one of the above models.

    obj_dict - the dict to convert

    Returns the Story, Issue, or Category version
    """
    content_object = instanceFromRaw(obj_dict)
    model = modelFromRole(content_object)
    return model
app.jinja_env.filters['asModel'] = asModel
