from django.contrib.gis.db.backends.postgis.schema import PostGISSchemaEditor

from django_cockroachdb.schema import (
    DatabaseSchemaEditor as CockroachSchemaEditor,
)


class DatabaseSchemaEditor(CockroachSchemaEditor, PostGISSchemaEditor):
    pass
