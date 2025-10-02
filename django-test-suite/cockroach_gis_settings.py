from cockroach_settings import DATABASES, PASSWORD_HASHERS, SECRET_KEY, USE_TZ

__all__ = [
    'DATABASES',
    'PASSWORD_HASHERS',
    'SECRET_KEY',
    'USE_TZ',
]

DATABASES['default']['ENGINE'] = 'django_cockroachdb_gis'
DATABASES['other']['ENGINE'] = 'django_cockroachdb_gis'
