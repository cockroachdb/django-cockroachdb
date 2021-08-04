from django.contrib.gis.db.backends.postgis.operations import PostGISOperations

from django_cockroachdb.operations import (
    DatabaseOperations as CockroachOperations,
)


class DatabaseOperations(CockroachOperations, PostGISOperations):

    @property
    def gis_operators(self):
        ops = PostGISOperations.gis_operators.copy()
        # https://github.com/cockroachdb/cockroach/issues/56124
        del ops['contained']  # @
        # https://github.com/cockroachdb/cockroach/issues/57096
        del ops['exact']  # ~=
        del ops['same_as']  # ~=
        # https://github.com/cockroachdb/cockroach/issues/57092
        del ops['left']  # <<
        del ops['right']  # >>
        # https://github.com/cockroachdb/cockroach/issues/57098
        del ops['overlaps_above']  # |&>
        del ops['overlaps_below']   # &<|
        del ops['overlaps_left']  # &<
        del ops['overlaps_right']  # &>
        # https://github.com/cockroachdb/cockroach/issues/57095
        del ops['strictly_above']  # |>>
        del ops['strictly_below']  # <<|
        return ops

    unsupported_functions = {
        'AsGML',  # st_asgml(): https://github.com/cockroachdb/cockroach/issues/48877
        'AsKML',  # st_askml(geometry, int): https://github.com/cockroachdb/cockroach/issues/48881
        'AsSVG',  # st_assvg(): # https://github.com/cockroachdb/cockroach/issues/48883
        'GeometryDistance',  # <-> operator: https://github.com/cockroachdb/cockroach/issues/57099
    }
