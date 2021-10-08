from django.contrib.gis.db.backends.postgis.schema import PostGISSchemaEditor

from django_cockroachdb.schema import (
    DatabaseSchemaEditor as CockroachSchemaEditor,
)


class DatabaseSchemaEditor(CockroachSchemaEditor, PostGISSchemaEditor):
    def _create_index_sql(self, model, *, fields=None, **kwargs):
        s = super()._create_index_sql(model, fields=fields, **kwargs)
        # Remove unsupported GIST_GEOMETRY_OPS_ND opclass.
        if isinstance(s.parts['columns'], str) and s.parts['columns'].endswith(' GIST_GEOMETRY_OPS_ND'):
            s.parts['columns'] = s.parts['columns'].rstrip(' GIST_GEOMETRY_OPS_ND')
        return s
