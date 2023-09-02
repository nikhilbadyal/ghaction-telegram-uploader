"""Custom Exceptions."""
from typing import Any, Self


class UploaderError(Exception):
    """Base class for all the project errors."""

    message = "Default Error message."

    def __init__(self: Self, *args: Any, **kwargs: Any) -> None:
        if args:
            self.message = args[0]
        super().__init__(self.message)

    def __str__(self: Self) -> str:
        """Return error message."""
        return self.message


class RequestError(UploaderError):
    """Generic Request failure."""

    def __init__(self: Self, *args: Any, **kwargs: Any) -> None:
        """Initialize the DownloadFailure exception.

        Args:
        ----
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
                url (str, optional): The URL of the failed icon scraping. Defaults to None.
        """
        super().__init__(*args)
        self.url = kwargs.get("url", None)
