from common import *

DEBUG = False

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAIGSN5LP2MLIXYBYQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'rainmaker-hosted'
AWS_LOCATION = 'pa/site_media'

from S3 import CallingFormat
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'rainmaker_pa',
        'PORT': '6432', # PgBouncer port
        'HOST': 'ec2-23-22-202-70.compute-1.amazonaws.com',
        'USER': 'rainmaker_pa',
        'PASSWORD': '31c3234rdcopadYbvha'
    }
}

# Static
STATIC_URL = 'https://rainmaker-hosted.s3.amazonaws.com/pa/site_media/'

ADMIN_MEDIA_PREFIX = 'https://s3.amazonaws.com/rainmaker-hosted/pa/site_media/admin/'

# GEOS paths for GeoDjango and GDAL. Configured for our particular Heroku setup.
GEOS_LIBRARY_PATH = '/app/.geodjango/geos/lib/libgeos_c.so'
GDAL_LIBRARY_PATH = '/app/.geodjango/gdal/lib/libgdal.so'

# Caching
CACHE_MIDDLEWARE_SECONDS = 5 * 60 # 5 minutes

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache'
    }
}