from flask          import render_template, abort
from .main          import app
from .data_loader   import data_loader

import template_helpers

from .models        import Publication, modelFromRole

@app.route('/')
def index():
    return render_template(
        'index.html',
        publication=Publication(),
    )



@app.route('/<slug>/')
def page(slug):

    target_obj = data_loader.load(slug)
    if not target_obj:
        abort(404)

    # Choose template
    template_name = "{0}.html".format(target_obj.role)

    context = {
        target_obj.role: modelFromRole(target_obj)
    }

    return render_template(
        template_name,
        **context
    )
