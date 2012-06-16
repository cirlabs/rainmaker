from common import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'rainmaker_wa',
        'PORT': '6432', # PgBouncer port
        'HOST': 'data.apps.cironline.org',
        'USER': 'rainmaker',
        'PASSWORD': '31c3Ybvhvs'
    }
}

# Static
STATIC_URL = 'http://media.apps.cironline.org/rainmaker/site_media/'

ADMIN_MEDIA_PREFIX = 'http://media.apps.cironline.org/rainmaker/site_media/admin/'

# GEOS paths for GeoDjango and GDAL. Configured for our particular Heroku setup.
GEOS_LIBRARY_PATH = '/app/.geodjango/geos/lib/libgeos_c.so'
GDAL_LIBRARY_PATH = '/app/.geodjango/gdal/lib/libgdal.so'

# Caching
CACHE_MIDDLEWARE_SECONDS = 90 * 60 # 90 minutes

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache'
    }
}
