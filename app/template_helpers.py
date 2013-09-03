from app import app
import settings


app.jinja_env.globals.update(ENVIRONMENT=settings.ENVIRONMENT)


# Public: helper for including static media assets in templates.
#         `{{ static_url('images/file.jpg') }}`
#
# path - a String path to the asset, relative to the root of the static folder
#
# Returns the absolute URL to the asset.
def static_url(path):
    return u'{0}{1}'.format(settings.STATIC_URL, path)
app.jinja_env.globals.update(static_url=static_url)



# Public: helper for including user-uploaded media in templates.
#         `{{ media_url('images/file.jpg') }}`
#
# path - a String path to the asset, relative to the root of the media folder
#
# Returns the absolute URL to the asset.
def media_url(path):
    return u'{0}{1}'.format(settings.MEDIA_URL, path)
app.jinja_env.globals.update(media_url=media_url)




# Goes with Formwork's .item- variants.
def to_item_size(count):
    size_map = {
        1: 'full',
        2: 'half',
        3: 'third',
        4: 'quarter',
        5: 'fifth',
    }
    return size_map.get(count, 'full')
app.jinja_env.filters['to_item_size'] = to_item_size


from jinja2 import evalcontextfilter, Markup
from cgi import escape
@evalcontextfilter
def render_block(eval_ctx, block):
    result = u''
    if block.type == Text.type:
        result = u"<p>{0}</p>".format(block.content.replace('\n', '<br>'))
    elif block.type == Image.type:
        result = u"<img src=\"{0}\">".format(block.content.get('640', {}).get('url'))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
app.jinja_env.filters['render_block'] = render_block

from content.models import Text
@evalcontextfilter
def content_preview(eval_ctx, story, char_limit=400):
    content_preview = ''
    if story.description:
        content_preview = description[:char_limit]
        if len(description) > char_limit:
            content_preview += '&hellip;'
    else:
        content_preview_text_length = 0
        for block in story.content:
            if block and block.type == Text.type and block.role != 'pre':
                content = escape(block.content.lstrip().rstrip())
                if content:
                    if content_preview_text_length + len(content) > char_limit:
                        content = content[:char_limit - content_preview_text_length]
                    content_preview_text_length += len(content)
                    if content_preview_text_length >= char_limit:
                        content += '&hellip;'
                    content_preview += " <span class='preview-%s'>%s</span>" % (block.role, content,)
                    if content_preview_text_length >= char_limit:
                        break
    if eval_ctx.autoescape:
        content_preview = Markup(content_preview)
    return content_preview
app.jinja_env.filters['content_preview'] = content_preview








from content.models import Container, Text, Image, Embed, instanceFromRaw

def render_flatpage(post, link_title=False):
    published_post = post.get('published_json')
    post_html = []
    if published_post:
        post = Container(published_post)

    post_html += render_content_blocks(post.get('content'))

    return u''.join(post_html)



def render_content_blocks(content):
    content_html = []
    for block_raw in content:
        block = instanceFromRaw(block_raw)
        if block.type == Text.type:
            content_html.append(render_textblock(block))
        elif block.type == Image.type:
            content_html.append(render_imageblock(block))
        elif block.type == Embed.type:
            content_html.append(render_embedblock(block))
    return content_html

# TODO: move to py-layout?
def render_imageblock(block, classes=None, attrs=None):
    if not classes:
        classes = []
    if not attrs:
        attrs = {}

    for k, v in block.layout.items():
        classes.append(u"{0}-{1}".format(k,v))

    try:
        url = block.content['1280']['url']
    except KeyError:
        return u''
    else:
        caption_html = ''
        for a in block.get('annotations',[]):
            if a['type'] == 'caption':
                caption_html = u"<div class='Caption'>{0}</div>".format(a['content'])
        return u"""
            <div class='ImageBlock {classes}''>
                <div class='content'>
                    <img src='{url}'>
                    {caption_html}
                </div>
            </div>
            """.format(
                url=url,
                classes=u' '.join(classes),
                caption_html=caption_html,
            )

def render_embedblock(block):
    return ''

def render_textblock(block, classes=None, attrs=None):
    # because classes=[] in the sig is bad
    if not classes:
        classes = []
    if not attrs:
        attrs = {}
    TAGS = {
        'paragraph': 'p',
        'pre': 'p',
        'quote': 'p',
        'heading': 'h2',
    }
    arrs = ["{0}='{1}'".format(k,v) for k, v in attrs.items()]
    # TODO: layout classes
    classes.append(block.role)
    markup = u"<{tag} class='TextBlock {classes}' {attrs}>{content}</{tag}>".format(
            tag=TAGS[block.role],
            classes=u' '.join(classes),
            attrs=u' '.join(attrs),
            content=block.toHTML(),
        )
    return markup