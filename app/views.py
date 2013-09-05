from flask          import render_template, abort
from .data_loader   import data_loader
from .main          import app
from .models        import Publication, modelFromRole

import settings
import template_helpers



def _loadPublication():
    """
    Private: load the Publication specified in settings from the API.
    
    Returns the active Publication.
    """
    publication_container = data_loader.load(
            short_name=settings.PUBLICATION_SHORT_NAME
        )
    publication = Publication(publication_container)
    return publication



@app.route('/')
def index():
    return render_template(
        'index.html',
        publication = _loadPublication(),
    )



@app.route('/<slug>/')
def page(slug):

    target_obj = data_loader.load(slug=slug)
    if not target_obj:
        abort(404)

    # Choose template based on the role.
    template_name = "{0}.html".format(target_obj.role)

    context = {
        target_obj.role : modelFromRole(target_obj),
        'publication'   : _loadPublication(),
    }

    return render_template(
        template_name,
        **context
    )
