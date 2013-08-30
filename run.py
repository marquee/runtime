import sys
from app import app

if __name__ == '__main__':

    if 'show_routes' in sys.argv:
        for r in app.url_map.iter_rules():
            print r

    elif 'debug' in sys.argv:
        app.run(debug=True)

    else:
        app.run()
