from django.utils.timezone import get_fixed_timezone, utc


def utc_tzinfo_factory(offset):
    if offset != 0:
        return get_fixed_timezone(offset)
    return utc
