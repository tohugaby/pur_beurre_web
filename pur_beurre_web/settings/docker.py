from . import *

ALLOWED_HOSTS = ['127.0.0.1', os.getenv('DOMAIN_NAME')]

DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

STATIC_ROOT = '/var/www/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_USER'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}


EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

if os.environ.get('ADMIN'):
    ADMINS = os.environ.get('ADMIN').split(";")
