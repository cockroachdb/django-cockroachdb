__version__ = '2.2.3'

# Check Django compatibility before other imports which may fail if the
# wrong version of Django is installed.
from .utils import check_django_compatability

check_django_compatability()

from .functions import register_functions  # noqa

register_functions()
