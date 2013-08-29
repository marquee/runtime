from flask      import Flask, render_template, abort, redirect
import settings
import os

template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'templates'))
app = Flask(__name__, template_folder=template_folder)
app.config.from_object(settings)
