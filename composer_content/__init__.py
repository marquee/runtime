from content import Text, Image, Container


default_base_class_names = {
    Text.type   : 'TextBlock',
    Image.type  : 'ImageBlock',
    # Embed.type  : 'EmbedBlock',
}

# Override base_class_name to use different selectors
def renderBlock(block, classes=None, attrs=None, base_class_name=None):
    # because classes=[] in the sig is bad
    if not classes:
        classes = []
    if not attrs:
        attrs = {}
    if not base_class_name:
        base_class_name = default_base_class_names[block.type]

    attrs = ["{0}='{1}'".format(k,v) for k, v in attrs.items()]

    classes.append(base_class_name)

    for layout_properties in block.layout.items():
        classes.append("{0}-{1}-{2}".format(base_class_name, *layout_properties))

    if block.get('role'):
        classes.append(u"{0}-{1}".format(base_class_name, block.role))

    if block.type == Image.type:
        template = u"<{tag} class='{classes}' {attrs}>"
        content = u''
        attrs.append("src='{0}'".format(_pickImageSrc(block)))
    elif block.type == Text.type:
        template = u"<{tag} class='{classes}' {attrs}>{content}</{tag}>"
        content = _renderBlockContent(block)


    markup = template.format(
            tag         = _pickTag(block),
            classes     = u' '.join(classes),
            attrs       = u' '.join(attrs),
            content     = content
        )
    return markup


def _pickImageSrc(block):
    return block.content.get('640', {}).get('url')

def _pickTag(block):
    if block.type == Text.type:
        TAGS = {
            'paragraph' : 'p',
            'pre'       : 'p',
            'quote'     : 'p',
            'heading'   : 'h2',
        }
        return TAGS.get(block.role, 'p')
    elif block.type == Image.type:
        return 'img'

def _renderBlockContent(block):
    return block.toHTML()
