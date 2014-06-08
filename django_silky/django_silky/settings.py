import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'ey5!m&h-uj6c7dzp@(o1%96okkq4!&bjja%oi*v3r=2t(!$7os'

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

TEMPLATE_DEBUG = True

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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware'
)

ROOT_URLCONF = 'django_silky.urls'

WSGI_APPLICATION = 'django_silky.wsgi.application'

DB_NAME = os.path.join(BASE_DIR, 'db.sqlite3')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_NAME,
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
        # 'silk': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG'
        # }
    },
}

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = '/tmp/static/'

MEDIA_ROOT = BASE_DIR + '/media/'

TEMPLATE_DIRS = (
    BASE_DIR
)

# A tuple of template loader classes, specified as strings. Each Loader class
# knows how to import templates from a particular source.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

# A tuple of callables that are used to populate the context in RequestContext.
# These callables take a request object as their argument and return a dictionary of
# items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth'
)
