"""Atmos Energy Account Center client library."""

import logging
from datetime import datetime

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import requests
import xlrd

from .constants import (
    DEFAULT_BILLING_PERIOD,
    DEFAULT_USAGE_MONTHS,
    DOWNLOAD_CONTENT_TYPE,
    DOWNLOAD_URL,
    LOGIN_FORM_ID_URL,
    LOGIN_URL,
    LOGOUT_URL,
)

# Configure logger for debugging
_LOGGER = logging.getLogger(__name__)


class AtmosEnergy:
    """
    A class to interact with the Atmos Energy account center to retrieve usage data.

    Attributes:
        username (str): The username for the Atmos Energy account.
        password (str): The password for the Atmos Energy account.
    """

    def __init__(self, username: str, password: str):
        """
        Initialize the AtmosEnergy object with user credentials.

        Args:
            username (str): The username for the Atmos Energy account.
            password (str): The password for the Atmos Energy account.
        """
        self.username = username
        self.password = password

        self._session = requests.Session()

    def _request(
        self, url: str, method: str = 'GET', data: dict | None = None
    ) -> requests.Response:
        """
        Make an HTTP request through the session and log details.

        Args:
            url (str): The URL to send the request to.
            method (str): The HTTP method ('GET' or 'POST'). Defaults to 'GET'.
            data (dict, optional): Form data to send in a POST request. Defaults to None.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            requests.exceptions.HTTPError: If the response status code indicates an error.
        """
        _LOGGER.debug('Making %s request to %s', method, url)

        if method == 'POST':
            response = self._session.post(url, data=data)
        else:
            response = self._session.get(url)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            _LOGGER.error(
                'HTTP request failed: %s %s', response.status_code, response.reason
            )
            raise

        _LOGGER.debug(
            'Received %s response with status code %d',
            'binary'
            if DOWNLOAD_CONTENT_TYPE in response.headers.get('Content-Type', '')
            else 'text',
            response.status_code,
        )

        return response

    def _mk_download_url_string(self, billing_period: str) -> str:
        """
        Generate the URL for downloading usage data.

        Args:
            billing_period (str): The billing period.

        Returns:
            str: The generated download URL.
        """
        timestamp = datetime.today().strftime('%m%d%Y%H:%M:%S')
        return DOWNLOAD_URL.format(billing_period=billing_period, timestamp=timestamp)

    def _mk_billing_period_string(self, months_ago: int) -> str:
        """
        Generate the billing period string for usage data retrieval.

        Args:
            months_ago (int): The number of months ago to retrieve data for.
                If 0, returns 'Current'. Otherwise returns a month/year string
                for that many months in the past.

        Returns:
            str: The formatted billing period (e.g., 'Current' or 'December,2025').
        """
        if months_ago == 0:
            return DEFAULT_BILLING_PERIOD

        historical_period = datetime.today() - relativedelta(months=months_ago)
        return historical_period.strftime('%B,%Y')

    def _validate_response_content(self, response: requests.Response) -> None:
        """
        Validate the content type of the HTTP response.

        Args:
            response (requests.Response): The HTTP response object to validate.

        Raises:
            TypeError: If the Content-Type header is not 'application/vnd.ms-excel'.
        """
        content_type = response.headers.get('Content-Type', '')

        if DOWNLOAD_CONTENT_TYPE not in content_type:
            _LOGGER.error(
                'Unexpected content type: %s. Expected: %s',
                content_type,
                DOWNLOAD_CONTENT_TYPE,
            )
            raise TypeError('Unexpected Content Type')

    def _fmt_usage(self, raw_usage: bytes) -> list[tuple[int, float]]:
        """
        Parse raw Excel usage data into a structured format.

        Args:
            raw_usage (bytes): The raw usage data in Excel binary format.

        Returns:
            list[tuple[int, float]]: A list of tuples containing (Unix timestamp, reading).

        Raises:
            ValueError: If the workbook cannot be opened or parsed.
        """
        try:
            workbook = xlrd.open_workbook(file_contents=raw_usage)
            sheet = workbook.sheet_by_index(0)
        except xlrd.biffh.XLRDError as e:
            _LOGGER.error('Unable to open workbook', exc_info=True)
            raise ValueError('Unable to Open Workbook') from e

        _LOGGER.debug('Processing %d rows of usage data', sheet.nrows - 1)
        usage = []
        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            reading = row[1].value
            dt = datetime.strptime(str(row[3].value), '%m/%d/%Y')
            usage.append((int(dt.timestamp()), reading))

        return usage

    def login(self) -> None:
        """
        Authenticate with the Atmos Energy account center.

        Fetches the login form to extract the form ID, then submits credentials.

        Raises:
            ValueError: If the login form ID cannot be found or login fails.
        """
        _LOGGER.debug('Fetching login form to retrieve form ID')
        response = self._request(LOGIN_FORM_ID_URL)

        soup = BeautifulSoup(response.content, 'html.parser')
        form_id = soup.find('input', {'id': 'authenticate_formId'})
        if not form_id:
            _LOGGER.error('Could Not Find Login Form ID')
            raise ValueError('Could Not Find Login Form ID')

        _LOGGER.debug('Got form ID: %s', form_id.get('value'))

        login = {
            'username': self.username,
            'password': self.password,
            'formId': form_id.get('value'),
        }

        _LOGGER.debug('Submitting login form')
        response = self._request(LOGIN_URL, method='POST', data=login)
        if response.url == LOGIN_URL:
            _LOGGER.error('Login failed, please check your credentials')
            raise ValueError('Login Failed')

    def logout(self) -> None:
        """
        Log out of the Atmos Energy account and close the session.
        """
        _LOGGER.debug('Logging out of the Atmos Energy account')
        self._request(LOGOUT_URL)
        self._session.close()

    def get_current_usage(self) -> list[tuple[int, float]]:
        """
        Retrieve unbilled usage data for the current billing period.

        Makes a single API request to retrieve the current month's usage data.

        Returns:
            list[tuple[int, float]]: A list of tuples containing (Unix timestamp, reading).

        Raises:
            TypeError: If the response content type is invalid or workbook parsing fails.
        """
        billing_period = self._mk_billing_period_string(0)
        download_url = self._mk_download_url_string(billing_period)
        response = self._request(download_url)

        self._validate_response_content(response)

        return self._fmt_usage(response.content)

    def get_usage_history(self, months: int) -> list[tuple[int, float]]:
        """
        Retrieve historical usage data for multiple billing periods.

        Makes multiple API requests (one per billing period) to retrieve historical
        usage data for the specified number of months.

        Args:
            months (int): The number of billing periods to retrieve (e.g., 6 for 6 months).

        Returns:
            list[tuple[int, float]]: A list of tuples containing (Unix timestamp, reading)
                aggregated across all requested periods.

        Raises:
            TypeError: If the response content type is invalid or workbook parsing fails.
        """
        all_usage = []

        # Get data for each requested billing period
        for period_offset in range(months):
            billing_period = self._mk_billing_period_string(period_offset)
            download_url = self._mk_download_url_string(billing_period)
            response = self._request(download_url)

            self._validate_response_content(response)

            period_usage = self._fmt_usage(response.content)
            all_usage.extend(period_usage)

        return all_usage


__all__ = ['AtmosEnergy']
