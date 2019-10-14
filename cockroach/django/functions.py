from django.db.models import DateTimeField
from django.db.models.functions import Cast, Coalesce, StrIndex


def coalesce(self, compiler, connection, **extra_context):
    # When coalescing a timestamptz column and a Python datetime, the datetime
    # must be cast to timestamptz (DateTimeField) to avoid "incompatible
    # COALESCE expressions: expected 'YYYY-MM-DDTHH:MM:SS'::TIMESTAMP to be of
    # type timestamptz, found type timestamp".
    if self.output_field.get_internal_type() == 'DateTimeField':
        clone = self.copy()
        clone.set_source_expressions([
            Cast(expression, DateTimeField()) for expression in self.get_source_expressions()
        ])
        return super(Coalesce, clone).as_sql(compiler, connection, **extra_context)
    return self.as_sql(compiler, connection, **extra_context)


def register_functions():
    Coalesce.as_cockroachdb = coalesce
    StrIndex.as_cockroachdb = StrIndex.as_postgresql
