from flask      import render_template, abort
from .main      import app
from .models    import data_loader

@app.route('/')
def index():
    return render_template(
        'index.html',
    )

@app.route('/<slug>/')
def page(slug):

    target_obj = data_loader.load(slug=slug)
    if not target_obj:
        abort(404)

    # Choose template

    return render_template(
        'story.html',
        slug=slug,
    )
