"""
Django settings for template project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

"Base settings shared by all environments"""

from datetime import timedelta
import os
import dj_database_url


BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)


# AWS
AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
S3DIRECT_REGION = os.environ.get('S3DIRECT_REGION')
AWS_S3_HOST = os.environ.get('AWS_S3_HOST')

# HEROKU
HEROKU_STAGING_APP = os.environ.get('HEROKU_STAGING_APP')
HEROKU_PRODUCTION_APP = os.environ.get('HEROKU_PRODUCTION_APP')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = r'{{ secret_key }}'
# MOVE TO CONFIG FILE
SECRET_KEY = os.environ.get('SECRET_KEY')

# IMAGE COMPRESSION & RESIZING
TINYPNG = os.environ.get('TINYPNG')

# PUSH NOTIFICATION SERVICE
ONE_SIGNAL_REST_KEY = os.environ.get('ONE_SIGNAL_REST_KEY')
ONE_SIGNAL_APP_ID = os.environ.get('ONE_SIGNAL_APP_ID')

# SMS PROVIDER
TWILIO_ACCOUND_SID = os.environ.get('TWILIO_ACCOUND_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

PLIVO_AUTH_ID = os.environ.get('PLIVO_AUTH_ID')
PLIVO_AUTH_TOKEN = os.environ.get('PLIVO_AUTH_TOKEN')
PLIVO_PHONE_NUMBER = os.environ.get('PLIVO_PHONE_NUMBER')

# EMAIL PROVIDER
SENDGRID_HOST = os.environ.get('SENDGRID_HOST')
SENDGRID_HOST_USER = os.environ.get('SENDGRID_HOST_USER')
SENDGRID_HOST_PASSWORD = os.environ.get('SENDGRID_HOST_PASSWORD')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
    'localhost',
]

ADMIN_SITE_HEADER = '{{ project_name }}'


# ######### APPLICATION DEFINITION

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

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

LOCAL_APPS = (
    '{{project_name}}.apps.users',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ######### END APPLICATION DEFINITION

# ######### MIDDLEWARE CONFIGURATION

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ######### END MIDDLEWARE CONFIGURATION

ROOT_URLCONF = '%s.urls' % r'{{ project_name }}'

# ######### WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
# ######### END WSGI CONFIGURATION


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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['{{project_name}}/templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ######### AWS, STATIC, TEMPLATE CONFIGURATION

STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False


S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
STATIC_ROOT = ''

STATICFILES_DIRS = (
    BASE_DIR('{{project_name}}', 'static'),
)

# ######### END AWS, STATIC, TEMPLATE CONFIGURATION

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

########## LOGGING CONFIGURATION
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
########## END LOGGING CONFIGURATION


########## REST FRAMEWORK CONFIGURATION
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.TokenAuthentication',
#     ),
#     # 'DEFAULT_RENDERER_CLASSES': (
#     #     'rest_framework.renderers.JSONRenderer',
#     # ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
#     'PAGINATE_BY': 10
# }
########## END REST FRAMEWORK CONFIGURATION

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ######### CORS CONFIGURATION
# CORS_ORIGIN_ALLOW_ALL = False
# # CORS_URLS_REGEX = r'^/api/.*$'
# CORS_ALLOW_CREDENTIALS = True
#
# CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://)?(\w+\.)?domain\.com$', )
#
# CORS_ORIGIN_WHITELIST = (
#     'localhost:9000',
# )

# ######### END CORS CONFIGURATION

# ######### S3 DIRECT

# UPLOAD_PATH = '{}'.format(uuid.uuid4())
#
# S3DIRECT_DESTINATIONS = {
#     # Allow anybody to upload any MIME type
#     'destination': {
#         'key': 'uploads/sub-path/{}'.format(UPLOAD_PATH),
#     },
#
# }
#
# S3DIRECT_UNIQUE_RENAME = False

# ######### END S3 DIRECT



