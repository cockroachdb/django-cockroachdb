import django
from django.core.exceptions import ImproperlyConfigured
from django.utils.version import get_version_tuple


def check_django_compatability():
    """
    Verify that this version of django-cockroachdb is compatible with the
    installed version of Django. For example, any django-cockroachdb 2.2.x is
    compatible with Django 2.2.y.
    """
    from . import __version__
    if django.VERSION[:2] != get_version_tuple(__version__)[:2]:
        raise ImproperlyConfigured(
            'You must use the latest version of django-cockroachdb {A}.{B}.x '
            'with Django {A}.{B}.y (found django-cockroachdb {C}).'.format(
                A=django.VERSION[0],
                B=django.VERSION[1],
                C=__version__,
            )
        )
