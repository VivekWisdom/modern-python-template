"""Client for the wikipedia REST API, version 1.

See `API documentation <https://en.wikipedia.org/api/rest_v1/#/>`_.
"""
from dataclasses import dataclass

import click
import desert
import marshmallow
import requests


API_URL: str = "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"


@dataclass
class Page:
    """Page Resource.

    Attributes:
        title: The title of the wikipedia page.
        extract: A plain text summary.
    """

    title: str
    extract: str


schema = desert.schema(Page, meta={"unknown": marshmallow.EXCLUDE})


def random_page(language: str = "en") -> Page:
    """Return a random page.

    Performs a GET request to the page/random/summary endpoint.

    Args:
        language (str, optional): The wikipedia language edition. Defaults to "en".

    Raises:
        click.ClickException: The HTTP request failed or HTTP response contained an invalid body.

    Returns:
        Page: A page resource.
    """
    url = API_URL.format(language=language)

    try:
        with requests.get(url) as response:
            response.raise_for_status()
            data = response.json()
            return schema.load(data)
    except (requests.RequestException, marshmallow.ValidationError) as error:
        message = str(error)
        raise click.ClickException(message) from error
