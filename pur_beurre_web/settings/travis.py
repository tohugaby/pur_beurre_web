from . import *

JSON_DIR_NAME = 'test_cached_json_files'
JSON_DIR_PATH = os.path.join(BASE_DIR, JSON_DIR_NAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'travis_ci_test',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432'
    }
}
