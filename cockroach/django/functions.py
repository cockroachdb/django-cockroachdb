from django.db.models.functions import StrIndex


def register_functions():
    StrIndex.as_cockroachdb = StrIndex.as_postgresql
