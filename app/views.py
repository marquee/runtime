from flask          import render_template, abort
from .data_loader   import data_loader
from .main          import app

from hyperdrive.models import Publication, Story, modelFromRole

from hyperdrive.storyset import StorySet

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
    publication = Publication()

    print len(publication.categories())
    return render_template(
        'index.html',
        publication = publication,
        categories  = publication.categories(),
    )


@app.route('/category/<slug>/')
def category(slug):
    publication = Publication()

    category_obj = publication.get_category(slug)

    if not category_obj:
        abort(404)

    template_name = 'category.html'


    context = {
        'publication'   : publication,
        'categories'    : publication.categories(),
        'category'      : category_obj,
    }

    return render_template(
        template_name,
        **context
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
        'publication'   : Publication(),
    }

    return render_template(
        template_name,
        **context
    )
