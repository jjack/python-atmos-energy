"""Unit tests for the AtmosEnergy class."""

# pylint: disable=protected-access, redefined-outer-name

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from atmos_energy import AtmosEnergy
from atmos_energy.constants import (
    DOWNLOAD_CONTENT_TYPE,
    DOWNLOAD_URL,
    LOGIN_FORM_ID_URL,
    LOGIN_URL,
    LOGGED_IN_URL,
    LOGOUT_URL,
)

# Expected output from processing the test Excel file
usage_xls_data = [
    (1762473600, '0.0'),
    (1762560000, '0.0'),
    (1762646400, '0.0'),
    (1762732800, '1.0'),
    (1762819200, '0.0'),
    (1762905600, '0.0'),
    (1762992000, '0.0'),
    (1763078400, '1.0'),
    (1763164800, '0.0'),
    (1763251200, '0.0'),
    (1763337600, '0.0'),
    (1763424000, '1.0'),
    (1763510400, '0.0'),
    (1763596800, '0.0'),
    (1763683200, '0.0'),
    (1763769600, '1.0'),
    (1763856000, '0.0'),
    (1763942400, '0.0'),
    (1764028800, '0.0'),
    (1764115200, '1.0'),
    (1764201600, '0.0'),
    (1764288000, '0.0'),
    (1764374400, '1.0'),
    (1764460800, '0.0'),
    (1764547200, '0.0'),
    (1764633600, '0.0'),
    (1764720000, '2.0'),
    (1764806400, '2.0'),
    (1764892800, '0.0'),
]


@pytest.fixture
def atmos_client():
    """Fixture to create an AtmosEnergy instance."""
    return AtmosEnergy(username='test_user', password='test_pass')


class TestAtmosEnergyInit:
    """Tests for AtmosEnergy initialization."""

    def test_init_stores_credentials(self):
        """Test that credentials are stored on initialization."""
        client = AtmosEnergy(username='testuser', password='testpass')
        assert client.username == 'testuser'
        assert client.password == 'testpass'

    def test_init_creates_session(self):
        """Test that Session object is created."""
        client = AtmosEnergy(username='user', password='pass')
        assert client._session is not None


class TestRequest:
    """Tests for the _request method."""

    @patch('atmos_energy.requests.Session.get')
    def test_request_get(self, mock_session_get, atmos_client):
        """Test GET request."""
        mock_response = MagicMock(status_code=200)
        mock_session_get.return_value = mock_response

        result = atmos_client._request('http://example.com')

        mock_session_get.assert_called_once_with('http://example.com')
        assert result == mock_response

    @patch('atmos_energy.requests.Session.post')
    def test_request_post(self, mock_session_post, atmos_client):
        """Test POST request."""
        mock_response = MagicMock(status_code=200)
        mock_session_post.return_value = mock_response

        data = {'key': 'value'}
        result = atmos_client._request(
            'http://example.com', method='POST', data=data)

        mock_session_post.assert_called_once_with(
            'http://example.com', data=data)
        assert result == mock_response

    @patch('atmos_energy.requests.Session.get')
    def test_request_http_error(self, mock_session_get, atmos_client):
        """Test handling of HTTP errors."""
        mock_response = MagicMock(status_code=401)
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError(response=mock_response)
        )
        mock_response.reason = 'Unauthorized'
        mock_session_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            atmos_client._request('http://example.com')


class TestMkDownloadUrlString:
    """Tests for the _mk_download_url_string method."""

    @patch('atmos_energy.datetime')
    def test_mk_download_url_string_current(self, mock_datetime, atmos_client):
        """Test URL generation for current period."""
        mock_datetime.today.return_value.strftime.return_value = '12102025120000'
        url = atmos_client._mk_download_url_string('Current')
        # pylint: disable=line-too-long
        assert (
            url
            == 'https://www.atmosenergy.com/accountcenter/usagehistory/dailyUsageDownload.html?&billingPeriod=Current&12102025120000'
        )

    @patch('atmos_energy.datetime')
    def test_mk_download_url_string_with_period(self, mock_datetime, atmos_client):
        """Test URL generation with specific billing period."""
        mock_datetime.today.return_value.strftime.return_value = '12102025120000'
        url = atmos_client._mk_download_url_string('December,2025')
        assert 'billingPeriod=December' in url


class TestMkBillingPeriodString:
    """Tests for the _mk_billing_period_string method."""

    def test_mk_billing_period_string_current(self, atmos_client):
        """Test billing period string for current month (0 months ago)."""
        period = atmos_client._mk_billing_period_string(0)
        assert period == 'Current'

    def test_mk_billing_period_string_historical(self, atmos_client):
        """Test billing period string for historical data (2 months ago)."""
        with patch('atmos_energy.datetime') as mock_datetime:
            from datetime import datetime  # pylint: disable=import-outside-toplevel

            mock_datetime.today.return_value = datetime(2025, 12, 10)
            period = atmos_client._mk_billing_period_string(2)
            assert ',' in period  # Format is "Month,Year"
            assert '2025' in period


class TestValidateResponseContent:
    """Tests for the _validate_response_content method."""

    def test_validate_response_content_valid(self, atmos_client):
        """Test validation with correct content type."""
        response = MagicMock(headers={'Content-Type': DOWNLOAD_CONTENT_TYPE})
        # Should not raise
        atmos_client._validate_response_content(response)

    def test_validate_response_content_invalid(self, atmos_client):
        """Test validation with incorrect content type."""
        response = MagicMock(headers={'Content-Type': 'text/html'})
        with pytest.raises(Exception, match='Unexpected Content Type'):
            atmos_client._validate_response_content(response)

    def test_validate_response_content_missing_header(self, atmos_client):
        """Test validation with missing Content-Type header."""
        response = MagicMock(headers={})
        with pytest.raises(Exception, match='Unexpected Content Type'):
            atmos_client._validate_response_content(response)


class TestFmtUsage:
    """Tests for the _fmt_usage method."""

    def test_fmt_usage_valid(self, atmos_client):
        """Test parsing valid Excel usage data."""
        path = Path(__file__).parent.resolve() / 'data' / 'usage.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        processed = atmos_client._fmt_usage(raw_usage)

        assert processed == usage_xls_data
        assert len(processed) == len(usage_xls_data)
        assert all(isinstance(item[0], int) for item in processed)
        assert all(isinstance(item[1], str) for item in processed)

    def test_fmt_usage_invalid_format(self, atmos_client):
        """Test error handling with invalid workbook format."""
        path = Path(__file__).parent.resolve() / 'data' / 'invalidformat.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        with pytest.raises(Exception, match='Unable to Open Workbook'):
            atmos_client._fmt_usage(raw_usage)


class TestLogin:
    """Tests for the login method."""

    @patch('atmos_energy.requests.Session.get')
    @patch('atmos_energy.requests.Session.post')
    def test_login_success(self, mock_session_post, mock_session_get, atmos_client):
        """Test successful login."""
        form_id = 'areallyawesomeformid'

        # pylint: disable=line-too-long
        mock_get_response = MagicMock(
            content=f'<input type="hidden" name="formId" value="{form_id}" id="authenticate_formId"/>',
            url=LOGIN_FORM_ID_URL,
            status_code=200,
        )
        mock_session_get.return_value = mock_get_response

        mock_post_response = MagicMock(
            url=LOGGED_IN_URL,
            status_code=200,
        )
        mock_session_post.return_value = mock_post_response

        atmos_client.login()

        mock_session_get.assert_called_once_with(LOGIN_FORM_ID_URL)
        mock_session_post.assert_called_once_with(
            LOGIN_URL,
            data={
                'username': atmos_client.username,
                'password': atmos_client.password,
                'formId': form_id,
            },
        )

    @patch('atmos_energy.requests.Session.get')
    def test_login_missing_form_id(self, mock_session_get, atmos_client):
        """Test login error when form ID is missing."""
        mock_get_response = MagicMock(
            content='<html>no form id here</html>',
            url=LOGIN_FORM_ID_URL,
            status_code=200,
        )
        mock_session_get.return_value = mock_get_response

        with pytest.raises(Exception, match='Could Not Find Login Form ID'):
            atmos_client.login()

    @patch('atmos_energy.requests.Session.get')
    @patch('atmos_energy.requests.Session.post')
    def test_login_invalid_credentials(
        self, mock_session_post, mock_session_get, atmos_client
    ):
        """Test login error with invalid credentials."""
        form_id = 'areallyawesomeformid'

        # pylint: disable=line-too-long
        mock_get_response = MagicMock(
            content=f'<input type="hidden" name="formId" value="{form_id}" id="authenticate_formId"/>',
            url=LOGIN_FORM_ID_URL,
            status_code=200,
        )
        mock_session_get.return_value = mock_get_response

        mock_post_response = MagicMock(
            url=LOGIN_URL,  # Still on login page = failed login
            content='<html>this is the login page</html>',
            status_code=200,
        )
        mock_session_post.return_value = mock_post_response

        with pytest.raises(Exception, match='Login Failed'):
            atmos_client.login()


class TestLogout:
    """Tests for the logout method."""

    @patch('atmos_energy.requests.Session.get')
    @patch('atmos_energy.requests.Session.close')
    def test_logout_success(self, mock_session_close, mock_session_get, atmos_client):
        """Test successful logout."""
        mock_get_response = MagicMock(
            content='<html>this is the logout page</html>',
            url=LOGOUT_URL,
            status_code=200,
        )
        mock_session_get.return_value = mock_get_response

        atmos_client.logout()

        mock_session_get.assert_called_once_with(LOGOUT_URL)
        mock_session_close.assert_called_once()


class TestGetUsage:
    """Tests for the get_usage method."""

    @patch('requests.Session.get')
    def test_get_usage_current_month(self, mock_session_get, atmos_client):
        """Test retrieving current month usage (1 month)."""
        path = Path(__file__).parent.resolve() / 'data' / 'usage.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        mock_get_response = MagicMock(
            url=DOWNLOAD_URL,
            content=raw_usage,
            status_code=200,
            headers={'Content-Type': DOWNLOAD_CONTENT_TYPE},
            stream=True,
        )
        mock_session_get.return_value = mock_get_response

        processed = atmos_client.get_usage(1)

        assert processed == usage_xls_data
        mock_session_get.assert_called_once()

    @patch('requests.Session.get')
    def test_get_usage_multiple_months(self, mock_session_get, atmos_client):
        """Test retrieving multiple months of usage data."""
        path = Path(__file__).parent.resolve() / 'data' / 'usage.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        mock_get_response = MagicMock(
            url=DOWNLOAD_URL,
            content=raw_usage,
            status_code=200,
            headers={'Content-Type': DOWNLOAD_CONTENT_TYPE},
            stream=True,
        )
        mock_session_get.return_value = mock_get_response

        processed = atmos_client.get_usage(6)

        # Should return 6 copies of the data (one for each month)
        expected = usage_xls_data * 6
        assert processed == expected
        # Should make 6 requests (one for each month)
        assert mock_session_get.call_count == 6

    @patch('requests.Session.get')
    def test_get_usage_invalid_content_type(self, mock_session_get, atmos_client):
        """Test error handling when response has invalid content type."""
        mock_get_response = MagicMock(
            url=DOWNLOAD_URL,
            content=b'<html>error page</html>',
            status_code=200,
            headers={'Content-Type': 'text/html'},
        )
        mock_session_get.return_value = mock_get_response

        with pytest.raises(Exception, match='Unexpected Content Type'):
            atmos_client.get_usage(1)

    @patch('requests.Session.get')
    def test_get_usage_invalid_workbook(self, mock_session_get, atmos_client):
        """Test error handling with invalid workbook data."""
        path = Path(__file__).parent.resolve() / 'data' / 'invalidformat.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        mock_get_response = MagicMock(
            url=DOWNLOAD_URL,
            content=raw_usage,
            status_code=200,
            headers={'Content-Type': DOWNLOAD_CONTENT_TYPE},
            stream=True,
        )
        mock_session_get.return_value = mock_get_response

        with pytest.raises(Exception, match='Unable to Open Workbook'):
            atmos_client.get_usage(1)

    @patch('requests.Session.get')
    def test_get_usage_default_parameter(self, mock_session_get, atmos_client):
        """Test get_usage with default parameter (should retrieve current month)."""
        path = Path(__file__).parent.resolve() / 'data' / 'usage.xls'
        with open(path, 'rb') as f:
            raw_usage = f.read()

        mock_get_response = MagicMock(
            url=DOWNLOAD_URL,
            content=raw_usage,
            status_code=200,
            headers={'Content-Type': DOWNLOAD_CONTENT_TYPE},
            stream=True,
        )
        mock_session_get.return_value = mock_get_response

        # Call without specifying months parameter
        processed = atmos_client.get_usage()

        assert processed == usage_xls_data
