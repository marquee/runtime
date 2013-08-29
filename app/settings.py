import os, subprocess

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

REQUIRED_ENV = [
    'CONTENT_API_TOKEN',
    'CONTENT_API_ROOT',
    'STATIC_URL',
    'CACHE_SOFT_EXPIRY',
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

# App config
PORT                = int(os.environ.get('PORT', 5000))
HOST                = os.environ.get('HOST', '127.0.0.1')
DEBUG               = str(os.environ.get('DEBUG')).lower() in ('yes', 'true', '1')
PRODUCTION          = str(os.environ.get('PRODUCTION')).lower() in ('yes','true','1')
ENVIRONMENT         = os.environ.get('ENVIRONMENT', 'production')

COMMIT_HASH = os.environ.get('COMMIT_HASH', '')

REDIS_URL               = os.environ.get('REDIS_URL')
SECRET_KEY              = os.environ['SECRET_KEY']

# MEDIA

STATIC_URL              = os.environ['STATIC_URL']
MEDIA_URL               = os.environ['MEDIA_URL']
MEDIA_BUCKET            = os.environ['MEDIA_BUCKET']
MEDIA_KEY_PREFIX        = os.environ['MEDIA_KEY_PREFIX']

AWS_ACCESS_KEY_ID       = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY   = os.environ['AWS_SECRET_ACCESS_KEY']

# Content API config
CONTENT_API_TOKEN       = os.environ['CONTENT_API_TOKEN']
CONTENT_API_ROOT        = os.environ['CONTENT_API_ROOT']

CACHE_SOFT_EXPIRY       = int(os.environ['CACHE_SOFT_EXPIRY'])