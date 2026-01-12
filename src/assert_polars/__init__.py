"""checkpl - Simple inline data validation for Polars."""

from assert_polars.core import hello, verify
from assert_polars.errors import CheckError
from assert_polars.predicates import is_uniq

__version__ = "0.2"
__all__ = ["hello", "verify", "CheckError", "is_uniq", "__version__"]
