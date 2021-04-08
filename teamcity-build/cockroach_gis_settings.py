from cockroach_settings import (
    DATABASES, DEFAULT_AUTO_FIELD, PASSWORD_HASHERS, SECRET_KEY,
)

__all__ = ['DATABASES', 'DEFAULT_AUTO_FIELD', 'PASSWORD_HASHERS', 'SECRET_KEY']

DATABASES['default']['ENGINE'] = 'django_cockroachdb_gis'
DATABASES['other']['ENGINE'] = 'django_cockroachdb_gis'
