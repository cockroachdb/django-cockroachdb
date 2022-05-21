from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISDatabaseWrapper,
)

from django_cockroachdb.base import DatabaseWrapper as CockroachDatabaseWrapper

from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(CockroachDatabaseWrapper, PostGISDatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    def __init__(self, *args, **kwargs):
        # Skip PostGISDatabaseWrapper.__init__() to work around
        # https://code.djangoproject.com/ticket/34344.
        CockroachDatabaseWrapper.__init__(self, *args, **kwargs)
