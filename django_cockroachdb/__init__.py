from .functions import register_functions
from .lookups import patch_lookups
from .utils import check_django_compatability

__version__ = '3.1.1'

check_django_compatability()
patch_lookups()
register_functions()
