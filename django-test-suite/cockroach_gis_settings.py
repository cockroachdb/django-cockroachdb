from cockroach_settings import (
    DATABASES, DEFAULT_AUTO_FIELD, PASSWORD_HASHERS, SECRET_KEY, USE_TZ,
)

__all__ = [
    'DATABASES', 'DEFAULT_AUTO_FIELD', 'PASSWORD_HASHERS', 'SECRET_KEY',
    'USE_TZ',
]

DATABASES['default']['ENGINE'] = 'django_cockroachdb_gis'
DATABASES['other']['ENGINE'] = 'django_cockroachdb_gis'
