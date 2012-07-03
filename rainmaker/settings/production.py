from common import *

DEBUG = False

# S3 and storages settings
# Fill these in if you want S3 storage enabled
DEFAULT_FILE_STORAGE = ''
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_LOCATION = '' # Subdirectory within your bucket. Works with boto.

from S3 import CallingFormat
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN

# Fill these in
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'rainmaker',
        'PORT': '',
        'HOST': '',
        'USER': '',
        'PASSWORD': ''
    }
}

# Static (Fill this in too)
STATIC_URL = ''

ADMIN_MEDIA_PREFIX = ''

# Caching (Fill this in too)
CACHE_MIDDLEWARE_SECONDS = 90 * 60 # 90 minutes

CACHES = {
    'default': {
        'BACKEND': ''
    }
}
