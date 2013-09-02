from flask          import render_template, abort
from .main          import app
from .data_loader   import data_loader

import template_helpers

from .models        import Publication, modelFromRole

import settings

def load_publication():
    publication_container = data_loader.load(
            short_name=settings.PUBLICATION_SHORT_NAME
        )
    publication = Publication(publication_container)
    return publication

@app.route('/')
def index():
    return render_template(
        'index.html',
        publication=load_publication(),
    )



@app.route('/<slug>/')
def page(slug):

    target_obj = data_loader.load(slug=slug)
    if not target_obj:
        abort(404)

    # Choose template
    template_name = "{0}.html".format(target_obj.role)

    context = {
        target_obj.role : modelFromRole(target_obj),
        'publication'   : load_publication(),
    }

    return render_template(
        template_name,
        **context
    )
