from app 			  import app
from app 		      import settings

from flask.ext.script import Manager
import sys

manager = Manager(app)

if settings.HYPERDRIVE:
	from hyperdrive.commands 	  import manager as hypermanager
	manager.add_command("hyperdrive", hypermanager)

if __name__ == '__main__':

    if 'show_routes' in sys.argv:
        for r in app.url_map.iter_rules():
            print r
    else:
    	manager.run()
