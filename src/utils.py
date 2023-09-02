"""Common utilities."""
from requests import Response

from src.constant import status_code_200
from src.exception import RequestError
from src.strings import request_failure


def handle_request_response(response: Response, url: str) -> None:
    """The function handles the response of a GET request and raises an exception if the response code is not 200.

    Parameters
    ----------
    response : Response
        The parameter `response` is of type `Response`, which is likely referring to a response object from
    an HTTP request. This object typically contains information about the response received from the
    server, such as the status code, headers, and response body.
    url: str
        The url on which request was made
    """
    response_code = response.status_code
    if response_code != status_code_200:
        msg = request_failure.format(response.text)
        raise RequestError(msg, url=url)
