from django.contrib.gis.db.models.functions import Distance, Length, Perimeter


def register_functions():
    Distance.as_cockroachdb = Distance.as_postgresql
    Length.as_cockroachdb = Length.as_postgresql
    Perimeter.as_cockroachdb = Perimeter.as_postgresql
