import os.path
from typing import Optional

import bs4
import requests

URL_BASE = 'https://content.govdelivery.com/bulletins/gd/{}'
CACHE_DIRECTORY = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), 'request_cache')


def _online_request(id_: str) -> str:
    """Online request for a govDelivery press release."""
    r = requests.get(URL_BASE.format(id_))
    if r.status_code == 200:
        return r.text
    raise ConnectionError('Could not retrieve govDelivery content.')


def _response_path(id_: str) -> str:
    """Path where the html response should be stored."""
    return os.path.join(CACHE_DIRECTORY, '{}.html'.format(id_))


def _save_response(id_: str, text: str) -> None:
    """Saves content response in local directory."""
    with open(_response_path(id_), 'w') as f:
        f.write(text)


def _read_response(id_: str) -> Optional[str]:
    """Attempts to read local, cached response."""
    resp_path = _response_path(id_)
    if os.path.isfile(resp_path):
        with open(resp_path) as f:
            return f.read()


def filter_content(base_html: bs4.Tag) -> bs4.Tag:
    """Limits the HTML content to the actual information."""
    return base_html.find('td', id='main-body')


def get_announcement(
    id_: str, filtered: bool = True, cached: bool = True) -> bs4.Tag:
    """Gets HTML content of a govDelivery page."""

    response = None

    if cached:
        response = _read_response(id_)

    if response is None:
        response = _online_request(id_)
        _save_response(id_, response)

    parsed_html = bs4.BeautifulSoup(response, 'html.parser')
    if filtered:
        parsed_html = filter_content(parsed_html)

    return parsed_html


if __name__ == "__main__":
    test_id = 'CALACOUNTY-29a2961'
    test_html = get_announcement(test_id)
