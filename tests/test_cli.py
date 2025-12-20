"""Unit tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from atmos_energy.cli import (
    format_timestamp,
    load_config,
    merge_config,
    print_table,
    write_csv,
)


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_format_timestamp_valid(self):
        """Test timestamp conversion to ISO format."""
        # Using a known timestamp
        timestamp = 1765398645
        result = format_timestamp(timestamp)
        assert '2025-12-10' in result
        assert 'T' in result  # ISO format includes T separator

    def test_format_timestamp_epoch(self):
        """Test epoch timestamp conversion."""
        timestamp = 0
        result = format_timestamp(timestamp)
        assert result.startswith('1970-01-01')


class TestWriteCsv:
    """Tests for write_csv function."""

    def test_write_csv_creates_file(self, tmp_path):
        """Test CSV file creation with correct format."""
        output_file = tmp_path / 'usage.csv'
        data = [
            (1765398645, 1.5),
            (1765485045, 2.0),
            (1765571445, 0.5),
        ]

        write_csv(data, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        lines = content.strip().split('\n')
        assert lines[0] == 'timestamp,value'
        assert len(lines) == 4

    def test_write_csv_format(self, tmp_path):
        """Test CSV output format with ISO timestamps."""
        output_file = tmp_path / 'usage.csv'
        data = [(1765398645, 1.5)]

        write_csv(data, str(output_file))

        content = output_file.read_text()
        lines = content.strip().split('\n')
        assert '2025-12-10' in lines[1] or '2025' in lines[1]
        assert '1.5' in lines[1]

    def test_write_csv_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if they don't exist."""
        output_file = tmp_path / 'subdir' / 'nested' / 'usage.csv'
        data = [(1765398645, 1.0)]

        write_csv(data, str(output_file))

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_write_csv_empty_data(self, tmp_path):
        """Test CSV file with empty data."""
        output_file = tmp_path / 'empty.csv'
        data = []

        write_csv(data, str(output_file))

        content = output_file.read_text()
        assert content == 'timestamp,value\n'


class TestPrintTable:
    """Tests for print_table function."""

    def test_print_table_output(self, capsys):
        """Test table output format."""
        data = [
            (1765398645, 1.5),
            (1765485045, 2.0),
        ]

        print_table(data)

        captured = capsys.readouterr()
        assert 'Timestamp' in captured.out
        assert 'Value' in captured.out
        assert '2025' in captured.out
        assert '1.5' in captured.out
        assert '2.0' in captured.out

    def test_print_table_header_separator(self, capsys):
        """Test that table has header separator."""
        data = [(1765398645, 1.0)]

        print_table(data)

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        # First line is header, second is separator
        assert 'Timestamp' in lines[0]
        assert '---' in lines[1]

    def test_print_table_empty_data(self, capsys):
        """Test table output with empty data."""
        data = []

        print_table(data)

        captured = capsys.readouterr()
        assert 'Timestamp' in captured.out
        assert 'Value' in captured.out


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_valid_yaml(self, tmp_path):
        """Test loading valid YAML config file."""
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('username: testuser\npassword: testpass\nmonths: 3\n')

        config = load_config(str(config_file))

        assert config['username'] == 'testuser'
        assert config['password'] == 'testpass'
        assert config['months'] == 3

    def test_load_config_file_not_found(self, tmp_path):
        """Test error when config file doesn't exist."""
        config_file = tmp_path / 'nonexistent.yaml'

        with pytest.raises(FileNotFoundError, match='Config file not found'):
            load_config(str(config_file))

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test error when YAML is invalid."""
        config_file = tmp_path / 'invalid.yaml'
        config_file.write_text('invalid: yaml: content: [')

        # YAML parsing raises YAMLError which is caught and re-raised as ValueError
        with pytest.raises(ValueError):
            load_config(str(config_file))

    def test_load_config_not_dict(self, tmp_path):
        """Test error when YAML doesn't contain a dictionary."""
        config_file = tmp_path / 'notdict.yaml'
        config_file.write_text('- item1\n- item2\n')

        with pytest.raises(ValueError, match='must contain a YAML dictionary'):
            load_config(str(config_file))

    def test_load_config_empty_file(self, tmp_path):
        """Test error when YAML file is empty."""
        config_file = tmp_path / 'empty.yaml'
        config_file.write_text('')

        with pytest.raises(ValueError, match='must contain a YAML dictionary'):
            load_config(str(config_file))


class TestMergeConfig:
    """Tests for merge_config function."""

    def test_merge_config_cli_precedence(self):
        """Test that CLI arguments take precedence over config file."""
        cli_args = MagicMock(
            username='cli_user',
            password='cli_pass',
            months=6,  # Explicitly set value (not default)
            output='cli.csv',  # Explicitly set value
        )
        config = {
            'username': 'config_user',
            'password': 'config_pass',
            'months': 3,
            'output': 'config.csv',
        }

        result = merge_config(cli_args, config)

        # CLI values should be preserved when explicitly set
        assert result.username == 'cli_user'
        assert result.password == 'cli_pass'
        assert result.months == 6
        assert result.output == 'cli.csv'

    def test_merge_config_fills_missing_values(self):
        """Test that config file fills in missing CLI values."""
        cli_args = MagicMock(
            username=None,
            password=None,
            months=1,
            output=None,
        )
        config = {
            'username': 'config_user',
            'password': 'config_pass',
            'months': 6,
            'output': 'config.csv',
        }

        result = merge_config(cli_args, config)

        assert result.username == 'config_user'
        assert result.password == 'config_pass'
        assert result.output == 'config.csv'

    def test_merge_config_months_default_replaced(self):
        """Test that default months value is replaced by config."""
        cli_args = MagicMock(
            username='user',
            password='pass',
            months=1,  # default value
            output=None,
        )
        config = {'months': 3}

        result = merge_config(cli_args, config)

        assert result.months == 3

    def test_merge_config_months_explicit_not_replaced(self):
        """Test that explicit CLI months value is not replaced."""
        cli_args = MagicMock(
            username='user',
            password='pass',
            months=6,  # explicitly set
            output=None,
        )
        config = {'months': 3}

        result = merge_config(cli_args, config)

        assert result.months == 6

    def test_merge_config_partial_config(self):
        """Test merging with partial config file."""
        cli_args = MagicMock(
            username=None,
            password='cli_pass',
            months=1,
            output=None,
        )
        config = {'username': 'config_user'}

        result = merge_config(cli_args, config)

        assert result.username == 'config_user'
        assert result.password == 'cli_pass'


class TestMainCli:
    """Tests for main CLI function."""

    @patch('atmos_energy.cli.AtmosEnergy')
    def test_main_current_usage_default(self, mock_atmos_class):
        """Test default behavior retrieves current month only (1 request)."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.get_current_usage.return_value = [(1765398645, 1.5)]
        mock_atmos_class.return_value = mock_client

        # Mock sys.argv
        with patch('sys.argv', ['cli', '--username', 'user', '--password', 'pass']):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            main()

        # Verify get_current_usage was called (no parameters - single request)
        mock_client.get_current_usage.assert_called_once_with()
        mock_client.login.assert_called_once()
        mock_client.logout.assert_called_once()

    @patch('atmos_energy.cli.AtmosEnergy')
    def test_main_historical_usage(self, mock_atmos_class):
        """Test retrieval of historical usage with --months flag (multiple requests)."""
        mock_client = MagicMock()
        mock_client.get_usage_history.return_value = [(1765398645, 1.5)] * 90
        mock_atmos_class.return_value = mock_client

        with patch(
            'sys.argv',
            ['cli', '--username', 'user', '--password', 'pass', '--months', '3'],
        ):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            main()

        # Verify get_usage_history was called with 3 months
        mock_client.get_usage_history.assert_called_once_with(3)

    @patch('atmos_energy.cli.AtmosEnergy')
    @patch('atmos_energy.cli.write_csv')
    def test_main_csv_output(self, mock_write_csv, mock_atmos_class):
        """Test CSV file output."""
        mock_client = MagicMock()
        data = [(1765398645, 1.5), (1765485045, 2.0)]
        mock_client.get_current_usage.return_value = data
        mock_atmos_class.return_value = mock_client

        with patch(
            'sys.argv',
            [
                'cli',
                '--username',
                'user',
                '--password',
                'pass',
                '--output',
                'usage.csv',
            ],
        ):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            main()

        mock_write_csv.assert_called_once_with(data, 'usage.csv')

    @patch('sys.argv', ['cli', '--username', 'user'])
    def test_main_missing_password(self):
        """Test error when password is missing."""
        from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2  # argparse error exit code

    @patch('sys.argv', ['cli', '--password', 'pass'])
    def test_main_missing_username(self):
        """Test error when username is missing."""
        from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2

    @patch('atmos_energy.cli.load_config')
    @patch('atmos_energy.cli.AtmosEnergy')
    def test_main_with_config_file(self, mock_atmos_class, mock_load_config):
        """Test using YAML config file for credentials."""
        mock_config = {
            'username': 'config_user',
            'password': 'config_pass',
            'months': 2,
        }
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.get_usage_history.return_value = [(1762263045, 1.5)] * 2
        mock_atmos_class.return_value = mock_client

        with patch('sys.argv', ['cli', '--config', 'config.yaml']):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            main()

        mock_load_config.assert_called_once_with('config.yaml')
        mock_client.login.assert_called_once()
        # Should call get_usage_history with 2 months since months=2 in config
        mock_client.get_usage_history.assert_called_once_with(2)

    @patch('atmos_energy.cli.load_config')
    def test_main_invalid_config_file(self, mock_load_config):
        """Test error handling for invalid config file."""
        mock_load_config.side_effect = FileNotFoundError('Config not found')

        with patch('sys.argv', ['cli', '--config', 'missing.yaml']):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    @patch('atmos_energy.cli.AtmosEnergy')
    def test_main_login_failure(self, mock_atmos_class):
        """Test error handling when login fails."""
        mock_client = MagicMock()
        mock_client.login.side_effect = Exception('Login Failed')
        mock_atmos_class.return_value = mock_client

        with patch('sys.argv', ['cli', '--username', 'user', '--password', 'pass']):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            with pytest.raises(SystemExit):
                main()

    @patch('atmos_energy.cli.AtmosEnergy')
    def test_main_verbose_logging(self, mock_atmos_class):
        """Test verbose logging flag."""
        mock_client = MagicMock()
        mock_client.get_current_usage.return_value = [(1762263045, 1.5)]
        mock_atmos_class.return_value = mock_client

        with patch(
            'sys.argv',
            ['cli', '--username', 'user', '--password', 'pass', '--verbose'],
        ):
            from atmos_energy.cli import main  # pylint: disable=import-outside-toplevel

            main()

        # Verify the function completes successfully with verbose flag
        mock_client.login.assert_called_once()
