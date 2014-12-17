"""
Django settings for template project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta
import os
import dj_database_url
import yaml

from djcelery import setup_loader


BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)


# load the application configuration file
APP_CONFIG_FILE = BASE_DIR('{{project_name}}', 'conf', 'app_config.yaml')
try:
    _CONFIGS = yaml.load(open(APP_CONFIG_FILE, 'r'))
    APP_CONFIG = _CONFIGS['APP']
except IOError:
    raise RuntimeError(
        """
        There was an error loading the application config file: %s \n
        Please make sure the file exists and does not contain errors \n.
        """ % APP_CONFIG_FILE
    )


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
    'localhost',
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = r'{{ secret_key }}'

# SECRET_KEY = APP_CONFIG.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = APP_CONFIG.get('DEBUG')

TEMPLATE_DEBUG = DEBUG

########## APPLICATION DEFINITION

DJANGO_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'taggit',
    'corsheaders',
    'imagekit',

    # Static file management:
    'compressor',

    # Asynchronous task queue:
    'djcelery',
)

LOCAL_APPS = (
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

########## END APPLICATION DEFINITION

########## MIDDLEWARE CONFIGURATION

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',    # This must be first on the list
    # Use GZip compression to reduce bandwidth.
    'django.middleware.gzip.GZipMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # This must be last
)

########## END MIDDLEWARE CONFIGURATION

ROOT_URLCONF = '%s.urls' % r'{{ project_name }}'

########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


DATABASE_URL = APP_CONFIG.get('DATABASE_URL')
TEST_DATABASE_URL = APP_CONFIG.get('TEST_DATABASE_URL')

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL),
    'test': dj_database_url.config(default=TEST_DATABASE_URL)
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

########## AWS, STATIC, TEMPLATE CONFIGURATION

STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False

AWS_S3_ACCESS_KEY_ID = APP_CONFIG.get('AWS_ACCESS_KEY')
AWS_S3_SECRET_ACCESS_KEY = APP_CONFIG.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = APP_CONFIG.get('AWS_STORAGE_BUCKET_NAME')

S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
STATIC_ROOT = ''

STATICFILES_DIRS = (
    BASE_DIR('{{project_name}}', 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = [BASE_DIR('{{project_name}}', 'templates')]

########## END AWS, STATIC, TEMPLATE CONFIGURATION

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '{{project_name}}.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        '{{project_name}}': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
########## END LOGGING CONFIGURATION


########## CELERY CONFIGURATION
# See: http://celery.readthedocs.org/en/latest/configuration.html#celery-task-result-expires
# CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=30)
#
# # See: http://docs.celeryproject.org/en/master/configuration.html#std:setting-CELERY_CHORD_PROPAGATES
# CELERY_CHORD_PROPAGATES = True
#
# # See: http://celery.github.com/celery/django/
# setup_loader()
#
# # See: http://docs.celeryproject.org/en/latest/configuration.html#broker-transport
# BROKER_TRANSPORT = 'amqplib'
#
# # Set this number to the amount of allowed concurrent connections on your AMQP
# # provider, divided by the amount of active workers you have.
# #
# # For example, if you have the 'Little Lemur' CloudAMQP plan (their free tier),
# # they allow 3 concurrent connections. So if you run a single worker, you'd
# # want this number to be 3. If you had 3 workers running, you'd lower this
# # number to 1, since 3 workers each maintaining one open connection = 3
# # connections total.
# #
# # See: http://docs.celeryproject.org/en/latest/configuration.html#broker-pool-limit
# BROKER_POOL_LIMIT = 3
#
# # See: http://docs.celeryproject.org/en/latest/configuration.html#broker-connection-max-retries
# BROKER_CONNECTION_MAX_RETRIES = 0
#
# # See: http://docs.celeryproject.org/en/latest/configuration.html#broker-url
# BROKER_URL = os.environ.get('RABBITMQ_URL') or os.environ.get('CLOUDAMQP_URL')
#
# # See: http://docs.celeryproject.org/en/latest/configuration.html#celery-result-backend
# CELERY_RESULT_BACKEND = 'amqp'
########## END CELERY CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #     'LOCATION': 'unix:/home/ubuntu/servers/{{project_name}}/{{project_name}}/run/memcached.sock',
    # }

    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': APP_CONFIG.get('REDIS_URL'),
    },
}
########## END CACHE CONFIGURATION


########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True

# See: http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_HASHING_METHOD
COMPRESS_CSS_HASHING_METHOD = 'content'

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
COMPRESS_CSS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
COMPRESS_JS_FILTERS = [
    'compressor.filters.template.TemplateFilter',
]

if not DEBUG:
    # See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
    COMPRESS_OFFLINE = True

    # See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
    COMPRESS_STORAGE = DEFAULT_FILE_STORAGE

    # See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_CSS_FILTERS
    COMPRESS_CSS_FILTERS += [
        'compressor.filters.cssmin.CSSMinFilter',
    ]

    # See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_JS_FILTERS
    COMPRESS_JS_FILTERS += [
        'compressor.filters.jsmin.JSMinFilter',
    ]

########## END COMPRESSION CONFIGURATION


########## DJANGO SUIT CONFIGURATION
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': '{{ project_name }}',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # forms
    # 'SHOW_REQUIRED_ASTERISK': True,  # Default True
    # 'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    # 'LIST_PER_PAGE': 15
}
########## END DJANGO SUIT CONFIGURATION


########## REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    # ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGINATE_BY': 10
}
########## END REST FRAMEWORK CONFIGURATION

########## SWAGGER SETTINGS
SWAGGER_SETTINGS = {
    "exclude_namespaces": [], # List URL namespaces to ignore
    "api_version": '0.1',  # Specify your API's version
    "api_path": "/api",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '', # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}
########## END SWAGGER SETTINGS

########## CORS CONFIGURATION
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_CREDENTIALS = True
########## END CORS CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'djblin@gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % '{{ project_name }}'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION


if DEBUG:
    ########## TOOLBAR CONFIGURATION
    # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
    INTERNAL_IPS = ('127.0.0.1',)

    # See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    ########## END TOOLBAR CONFIGURATION