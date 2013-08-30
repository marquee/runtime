import os, subprocess

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

REQUIRED_ENV = [
    'CONTENT_API_TOKEN',
    'CONTENT_API_ROOT',
    'STATIC_URL',
    'CACHE_SOFT_EXPIRY',
    'SECRET_KEY',
]

if not set(REQUIRED_ENV).issubset(os.environ):
    try:
        f = open('.env', 'r')
    except IOError:
        raise IOError('You are missing required environment variables')

    if f is not None:
        for line in f.readlines():
            split_line = line.split('=')
            var = split_line[0]
            if len(split_line) > 1:
                val = split_line[1].strip()
            else:
                val = ''
            os.environ[var] = val

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
CACHE_SOFT_EXPIRY       = int(os.environ['CACHE_SOFT_EXPIRY'])