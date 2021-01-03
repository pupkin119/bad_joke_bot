import os
import environ

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env('.env')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bots_bad_joke',
        'USER': 'developer',
        'PASSWORD' : '2010690',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

INSTALLED_APPS = (
    'bad_joke',
)

SECRET_KEY = 'v%4rh!_o64$mfb9qlv3z#v92r((ku&@(vcaj8gs0s!53ac2s8w'
