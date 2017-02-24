"""
production.pyDjango settings for template project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

from base import *
import yaml

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
    '*',
]

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True


# ######### APPLICATION DEFINITION

THIRD_PARTY_APPS = (
    # 'rest_framework',
    # 'rest_framework.authtoken',
    # 'taggit',
    # 'corsheaders',
    # 'storages',
    # 's3direct',
    # 'import_export',
    # 'django_rq'
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ######### END APPLICATION DEFINITION

# ######### END MIDDLEWARE CONFIGURATION

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}

# ######### DJANGO RQ CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    }
}

# ######### END DJANGO RQ CONFIGURATION



