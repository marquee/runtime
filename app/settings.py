"""
Load the configuration specified in the environment into names for use
elsewhere in the app. 
"""

import os



PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

# The minimum necessary configuration to run the app.
REQUIRED_ENV = [
    'CONTENT_API_TOKEN',
    'CONTENT_API_ROOT',
    'STATIC_URL',
    'CACHE_SOFT_EXPIRY',
    'SECRET_KEY',
    'PUBLICATION_SHORT_NAME',
]

# Load any additional configuration from an .env file if the environment
# doesn't already have everything required.
remaining_env_variables = set(REQUIRED_ENV)
if not set(REQUIRED_ENV).issubset(os.environ):
    try:
        f = open('.env', 'r')
    except IOError:
        raise IOError('You are missing a .env file')

    if f is not None:
        for line in f.readlines():
            split_line = line.split('=')
            var = split_line[0]
            if len(split_line) > 1:
                val = split_line[1].strip()
            else:
                val = ''
            os.environ[var] = val
            if var in remaining_env_variables:
                remaining_env_variables.remove(var)
    if len(remaining_env_variables) > 0:
        raise AttributeError('You are missing the following env variables: {0}'.format(
                    ', '.join(sorted(list(remaining_env_variables)))
                ))



# Some helpers for converting the environment values to the Python equivalent.

def asBool(var_name, default=None):
    if var_name in os.environ:
        return str(os.environ.get(var_name)).lower() in ('yes', 'true', '1')
    return default

def asInt(var_name, default=None):
    if var_name in os.environ:
        return int(os.environ.get(var_name))
    return default



# App config
PORT                    = asInt('PORT', 5000)
HOST                    = os.environ.get('HOST', '127.0.0.1')
DEBUG                   = asBool('DEBUG', False)
ENVIRONMENT             = os.environ.get('ENVIRONMENT', 'production')

REDIS_URL               = os.environ.get('REDIS_URL')
SECRET_KEY              = os.environ['SECRET_KEY']
STATIC_URL              = os.environ['STATIC_URL']

# Content API config
CONTENT_API_TOKEN       = os.environ['CONTENT_API_TOKEN']
CONTENT_API_ROOT        = os.environ['CONTENT_API_ROOT']
CACHE_SOFT_EXPIRY       = int(os.environ['CACHE_SOFT_EXPIRY'])  # minutes
PUBLICATION_SHORT_NAME  = os.environ['PUBLICATION_SHORT_NAME']
PUBLICATION_NAME        = os.environ.get('PUBLICATION_NAME', u'')
