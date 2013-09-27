from jinja2 import nodes, Markup
from jinja2.ext import Extension

import settings

class CDNTagExtension(Extension):
    tags = set(['cdn'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        args = [parser.parse_tuple(), nodes.Name('request', 'load'), nodes.Name('DEBUG', 'load')]
        return nodes.Output([
            self.call_method('_render', args),
        ]).set_lineno(lineno)

    def _render(self, libs, request, debug):
        print libs, debug
        if libs:
            if isinstance(libs, basestring):
                libs = (libs,)
            use_compressed = False
            use_minified = not settings.DEBUG
            if hasattr(request, 'accept_encodings'):
                use_compressed = 'gzip' in request.accept_encodings

            def _make_tag(lib):
                lib_name, lib_type = lib.rsplit('.', 1)
                lib_parts       = lib_name.split('-')
                lib_name        = lib_parts[0]
                lib_version     = lib_parts[1]
                force_minify    = len(lib_parts) > 2
                print lib_name, lib_version, lib_type, use_compressed

                if lib_type == 'css':
                    template = u'<link rel="stylesheet" type="text/css" href="{url}">'
                else:
                    template = u'<script src="{url}"></script>'

                if use_compressed:
                    lib_type += '.gz'
                if use_minified or force_minify:
                    lib_version += '-min'

                url = u"//{cdn_root}{name}-{version}.{type}".format(
                        cdn_root    = settings.LIB_CDN_ROOT,
                        name        = lib_name,
                        version     = lib_version,
                        type        = lib_type,
                    )
                return template.format(url=url)

            lib_tags = map(_make_tag, libs)
            return Markup(''.join(lib_tags))
        return ''
