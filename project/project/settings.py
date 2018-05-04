import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'ey5!m&h-uj6c7dzp@(o1%96okkq4!&bjja%oi*v3r=2t(!$7os'

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'silk',
    'example_app'
)

ROOT_URLCONF = 'project.urls'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware'
]

WSGI_APPLICATION = 'wsgi.application'

DB = os.environ['DB']
if DB == 'postgresql':
    DB = 'postgresql_psycopg2'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + DB,
        'NAME': os.environ['DB_NAME']
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'formatters': {
        'mosayc': {
            'format': '%(asctime)-15s %(levelname)-7s %(message)s [%(funcName)s (%(filename)s:%(lineno)s)]',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'mosayc'
        }
    },
    'loggers': {
        'silk': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    },
}

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = '/tmp/static/'

if not os.path.exists(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'

if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

SILKY_META = True
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
# Do not garbage collect for tests
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 0
# SILKY_AUTHENTICATION = True
# SILKY_AUTHORISATION = True

SILKY_DISTRIBUTION_TAB = True
