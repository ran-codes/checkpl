"""Custom exceptions for checkpl."""


class CheckError(Exception):
    """Raised when a data validation check fails.

    Attributes:
        check_name: Name of the check that failed (e.g., "is_uniq", "not_null")

    Example:
        try:
            df.pipe(is_uniq('id'))
        except CheckError as e:
            print(f"Check '{e.check_name}' failed: {e}")
    """

    def __init__(self, message: str, check_name: str | None = None):
        super().__init__(message)
        self.check_name = check_name
