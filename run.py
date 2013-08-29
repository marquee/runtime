import sys

from app                   import app

if 'debug' in sys.argv:
    app.run(debug=True)

if 'show_routes' in sys.argv:
    for r in app.url_map.iter_rules():
        print r
