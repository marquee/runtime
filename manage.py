""" Usage: manage.py COMMAND [-t <host>] [-p <port>] [--debug]

Options:
    --debug     watch for changes and reload app
    -t <host>   use an alternate host address
    -p <port>   use an alternate port number

Commands:
    runserver           run the Flask application

"""

from docopt import docopt

from app import app
from app import settings

import logging
import sys

# Colored Logging Formatter
# =========================
# Borrowed from http://mrqe.co/16uCGRh

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ   = "\033[0m"
COLOR_SEQ   = "\033[1;%dm"
BOLD_SEQ    = "\033[1m"
COLORS      = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
}


def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

class ColoredLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-2s$RESET][%(levelname)-4s] %(message)s"

    COLOR_FORMAT = formatter_message(FORMAT, True)
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return

logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger('runtime.manage')


# If hyperdrive hasn't been initiated, don't use it
try:
    from hyperdrive.commands    import manager as hypermanager
except ImportError:
    settings.HYPERDRIVE = False

AVAILABLE_COMMANDS = [
    'runserver'
]

# Main program loop
if __name__ == '__main__':
    arguments = docopt(__doc__, help=True)
    command   = arguments.get('COMMAND')
    app_kwrds = {}

    if command is None:
        print __doc__
        quit()

    if command not in AVAILABLE_COMMANDS:
        print "{0} is not an available command\n".format(command)
        print __doc__
        quit()

    if not settings.HYPERDRIVE:
        logger.warning('Hyperdrive not initiated')

    if settings.HYPERDRIVE:
        app_kwrds['hyperdrive'] = hypermanager

    if command == 'runserver':
        debug   = arguments.get('--debug')
        host    = arguments.get('-t')
        port    = arguments.get('-p')

        if host is None:
            host = settings.HOST

        if port is None:
            port = settings.PORT

        app.run(host=host, port=int(port), debug=debug)
