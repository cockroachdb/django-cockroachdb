from django.db.models.fields.json import HasKeyLookup, KeyTransform
from django.db.models.lookups import PostgresOperatorLookup


def patch_lookups():
    HasKeyLookup.as_cockroachdb = HasKeyLookup.as_postgresql
    KeyTransform.as_cockroachdb = KeyTransform.as_postgresql
    PostgresOperatorLookup.as_cockroachdb = PostgresOperatorLookup.as_postgresql
