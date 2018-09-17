import os
import random
import string
import dj_database_url
from . import *


SECRET_KEY_FILE_PATH = os.path.join(BASE_DIR, 'secret_key.txt')
if os.path.exists(SECRET_KEY_FILE_PATH):
    with open(SECRET_KEY_FILE_PATH, 'r') as secret:
        SECRET_KEY = secret.read()
else:
    SECRET_KEY = "".join([random.choice(string.printable) for _ in range(50)])
    with open(SECRET_KEY_FILE_PATH, 'w') as secret:
        secret.write(SECRET_KEY)

if os.environ.get('DEBUG'):
    DEBUG = os.environ.get('DEBUG')
else:
    DEBUG = False


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = ['purbeurretg.herokuapp.com']


MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware'
]


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

if os.environ.get('ADMIN'):
    ADMIN = os.environ.get('ADMIN').split(";")
