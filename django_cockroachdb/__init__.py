from .functions import register_functions
from .utils import check_django_compatability

__version__ = '2.2'

check_django_compatability()
register_functions()
