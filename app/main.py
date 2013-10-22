from flask  import Flask, render_template, abort, redirect
import os
import settings


template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'templates'))

app = Flask(
        __name__,
        template_folder = template_folder,
        static_url_path = '/static',
        static_folder   = '../static',
    )

app.jinja_env.add_extension('app.template_extensions.CDNTagExtension')

app.config.from_object(settings)



if settings.HYPERDRIVE:
	from hyperdrive.main import hyperdrive
	app.register_blueprint(hyperdrive, url_prefix="/hyperdrive")