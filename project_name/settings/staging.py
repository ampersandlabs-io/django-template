"""
production.pyDjango settings for template project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

from base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [

]

ADMIN_SITE_HEADER = '{{ project_name }}'

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

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASE_URL = os.environ.get('DATABASE_URL')

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}

# ######### LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             'datefmt': "%d/%b/%Y %H:%M:%S"
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR('logs', '{{project_name}}.log'),
#             'formatter': 'verbose'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'propagate': True,
#             'level': 'DEBUG',
#         },
#         '{{project_name}}': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#         },
#     }
# }
# ######### END LOGGING CONFIGURATION


# ######### DJANGO RQ CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches

# RQ_QUEUES = {
#     'default': {
#         'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),  # If you're on Heroku
#         'DEFAULT_TIMEOUT': 500,
#     }
# }

# ######### END DJANGO RQ CONFIGURATION



