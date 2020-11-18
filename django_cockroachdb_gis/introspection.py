from django.contrib.gis.db.backends.postgis.introspection import (
    PostGISIntrospection,
)

from django_cockroachdb.introspection import (
    DatabaseIntrospection as CockroachIntrospection,
)


class DatabaseIntrospection(CockroachIntrospection, PostGISIntrospection):
    pass
