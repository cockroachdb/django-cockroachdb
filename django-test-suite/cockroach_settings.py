import os

DATABASES = {
    'default': {
        'ENGINE': 'django_cockroachdb',
        'NAME': 'django_tests',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 26257,
        'OPTIONS': {},
    },
    'other': {
        'ENGINE': 'django_cockroachdb',
        'NAME': 'django_tests2',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 26257,
        'OPTIONS': {},
    },
}
if os.environ.get('USE_SERVER_SIDE_BINDING') == 'server_side_binding':
    DATABASES['default']['OPTIONS']['server_side_binding'] = True
    DATABASES['other']['OPTIONS']['server_side_binding'] = True

SECRET_KEY = 'django_tests_secret_key'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
USE_TZ = False
