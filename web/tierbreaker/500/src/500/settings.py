import os

DEBUG = os.environ.get('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')
TEMPLATE_DEBUG = DEBUG
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-key')
ROOT_URLCONF = '500.urls'
INSTALLED_APPS = ()
MIDDLEWARE_CLASSES = ()
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)
ALLOWED_HOSTS = ['*']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.path.join(os.path.dirname(__file__), 'challenge.sqlite3')}}
