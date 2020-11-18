from django_cockroachdb.base import DatabaseWrapper as CockroachDatabaseWrapper

from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(CockroachDatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
