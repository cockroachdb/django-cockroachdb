from django.db.models import (
    DateTimeField, DecimalField, FloatField, IntegerField,
)
from django.db.models.functions import (
    ACos, ASin, ATan, ATan2, Cast, Ceil, Coalesce, Cos, Cot, Degrees, Exp,
    Floor, Ln, Log, Radians, Round, Sin, Sqrt, StrIndex, Tan,
)


def atan2(self, compiler, connection, **extra_context):
    # This function is usually ATan2(y, x), returning the inverse tangent
    # of y / x, but it's ATan2(x, y) on cockroachdb (hence reversed()).
    clone = self.copy()
    clone.set_source_expressions([
        Cast(expression, FloatField()) if isinstance(expression.output_field, (DecimalField, IntegerField))
        else expression for expression in reversed(self.get_source_expressions()[::-1])
    ])
    return clone.as_sql(compiler, connection, **extra_context)


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


def float_cast(self, compiler, connection, **extra_context):
    # Most cockroachdb math functions require float arguments instead of
    # decimal or integer.
    clone = self.copy()
    clone.set_source_expressions([
        Cast(expression, FloatField()) if isinstance(expression.output_field, (DecimalField, IntegerField))
        else expression for expression in self.get_source_expressions()[::-1]
    ])
    return clone.as_sql(compiler, connection, **extra_context)


def register_functions():
    math_funcs_needing_float_cast = (
        ACos, ASin, ATan, ATan2, Ceil, Cos, Cot, Degrees, Exp, Floor, Ln, Log,
        Radians, Round, Sin, Sqrt, Tan,
    )
    for func in math_funcs_needing_float_cast:
        func.as_cockroachdb = float_cast
    ATan2.as_cockroachdb = atan2
    Coalesce.as_cockroachdb = coalesce
    StrIndex.as_cockroachdb = StrIndex.as_postgresql
