from django.contrib.gis.db.backends.postgis.features import (
    DatabaseFeatures as PostGISFeatures,
)
from django.utils.functional import cached_property

from django_cockroachdb.features import DatabaseFeatures as CockroachFeatures


class DatabaseFeatures(CockroachFeatures, PostGISFeatures):
    supports_3d_storage = False
    supports_3d_functions = False
    supports_raster = False
    # Not supported: https://github.com/cockroachdb/cockroach/issues/57092
    supports_left_right_lookups = False
    # unimplemented: column point is of type geometry and thus is not indexable
    # https://go.crdb.dev/issue/35730
    supports_geometry_field_unique_index = False

    @cached_property
    def django_test_expected_failures(self):
        expected_failures = super().django_test_expected_failures
        expected_failures.update({
            # ST_AsText output different from PostGIS (extra space):
            # https://github.com/cockroachdb/cockroach/issues/53651
            'gis_tests.geoapp.test_functions.GISFunctionsTests.test_aswkt',
            # Unsupported ~= (same_as/exact) operator:
            # https://github.com/cockroachdb/cockroach/issues/57096
            'gis_tests.geoapp.tests.GeoLookupTest.test_equals_lookups',
            'gis_tests.geoapp.tests.GeoLookupTest.test_null_geometries_excluded_in_lookups',
            'gis_tests.relatedapp.tests.RelatedGeoModelTest.test06_f_expressions',
            # unknown signature: st_union(geometry, geometry)
            # https://github.com/cockroachdb/cockroach/issues/49064
            'gis_tests.distapp.tests.DistanceTest.test_dwithin',
            'gis_tests.geoapp.test_functions.GISFunctionsTests.test_diff_intersection_union',
            'gis_tests.geoapp.test_functions.GISFunctionsTests.test_union_mixed_srid',
            'gis_tests.geoapp.test_functions.GISFunctionsTests.test_union',
            'gis_tests.geoapp.tests.GeoLookupTest.test_gis_lookups_with_complex_expressions',
            'gis_tests.geoapp.tests.GeoLookupTest.test_relate_lookup',
            # Time zone issue with dates before 1883:
            # https://github.com/cockroachdb/cockroach/issues/54294
            'gis_tests.geoapp.test_regress.GeoRegressionTests.test_unicode_date',
            # NotSupportedError: this box2d comparison operator is experimental
            'gis_tests.geoapp.tests.GeoLookupTest.test_contains_contained_lookups',
            # unknown signature: st_dwithin(geography, geometry, decimal) (desired <bool>)
            # https://github.com/cockroachdb/cockroach/issues/53720
            'gis_tests.geogapp.tests.GeographyTest.test02_distance_lookup',
            # unknown signature: st_distancespheroid(geometry, geometry, string)
            # https://github.com/cockroachdb/cockroach/issues/48922#issuecomment-693096502
            'gis_tests.distapp.tests.DistanceTest.test_distance_lookups_with_expression_rhs',
            'gis_tests.distapp.tests.DistanceTest.test_geodetic_distance_lookups',
            'gis_tests.distapp.tests.DistanceFunctionsTests.test_distance_geodetic_spheroid',
            # st_lengthspheroid(): unimplemented:
            # https://github.com/cockroachdb/cockroach/issues/48968
            'gis_tests.distapp.tests.DistanceFunctionsTests.test_length',
            # Unsupported ~= (https://github.com/cockroachdb/cockroach/issues/57096)
            # and @ operators (https://github.com/cockroachdb/cockroach/issues/56124).
            'gis_tests.geogapp.tests.GeographyTest.test04_invalid_operators_functions',
        })
        return expected_failures
