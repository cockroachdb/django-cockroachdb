DATABASES = {
    'default': {
        'ENGINE': 'django_cockroachdb',
        'NAME': 'django_tests',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 26257,
    },
    'other': {
        'ENGINE': 'django_cockroachdb',
        'NAME': 'django_tests2',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 26257,
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
SECRET_KEY = 'django_tests_secret_key'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
USE_TZ = False
