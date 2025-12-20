"""Command-line interface for AtmosEnergy."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

from atmos_energy import AtmosEnergy

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)


def format_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to human-readable ISO format.

    Args:
        timestamp (int): Unix timestamp (seconds since epoch).

    Returns:
        str: ISO format timestamp (e.g., '2025-12-10T15:30:45').
    """
    return datetime.fromtimestamp(timestamp).isoformat()


def write_csv(data: list[tuple[int, float]], output_file: str) -> None:
    """Write usage data to a CSV file.

    Creates parent directories if they don't exist.

    Args:
        data (list[tuple[int, float]]): List of (timestamp, value) tuples.
        output_file (str): Path to output CSV file.

    Raises:
        IOError: If the file cannot be written.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('timestamp,value\n')
        for timestamp, value in data:
            f.write(f'{format_timestamp(timestamp)},{value}\n')

    _LOGGER.debug('Data written to %s', output_path)


def print_table(data: list[tuple[int, float]]) -> None:
    """Print usage data as a formatted console table.

    Args:
        data (list[tuple[int, float]]): List of (timestamp, value) tuples.
    """
    print(f'{"Timestamp":<30} {"Value":<10}')
    print('-' * 40)
    for timestamp, value in data:
        print(f'{format_timestamp(timestamp):<30} {value:<10}')


def load_config(config_file: str) -> dict:
    """Load configuration from YAML file.

    Args:
        config_file: Path to YAML config file

    Returns:
        Dictionary with configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If YAML is invalid or config is not a dictionary
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f'Config file not found: {config_file}')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f'Invalid YAML in config file: {e}') from e

    if not isinstance(config, dict):
        raise ValueError('Config file must contain a YAML dictionary')

    return config


def merge_config(cli_args: argparse.Namespace, config: dict) -> argparse.Namespace:
    """Merge CLI arguments with config file values.

    CLI arguments take precedence over config file values.

    Args:
        cli_args: Parsed command-line arguments
        config: Configuration dictionary

    Returns:
        Updated Namespace with merged values
    """
    # Set credentials from config if not provided via CLI
    if not cli_args.username:
        cli_args.username = config.get('username')
    if not cli_args.password:
        cli_args.password = config.get('password')

    # Set other options from config if not provided via CLI
    if cli_args.months == 1 and config.get('months'):
        cli_args.months = config.get('months')
    if not cli_args.output and config.get('output'):
        cli_args.output = config.get('output')

    return cli_args


def main():
    """Main CLI entry point for retrieving Atmos Energy usage data.

    Authenticates with the Atmos Energy account center and retrieves usage data.
    Outputs to console table by default, or to CSV file if --output is specified.
    Supports credentials via --username/--password or YAML config file.

    Exits with code 1 on error (missing credentials, config error, API error).
    """
    parser = argparse.ArgumentParser(
        description='Retrieve Atmos Energy usage data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Config file format (YAML):
  username: your_username
  password: your_password
  months: 3
  output: usage.csv

Example usage:
  atmos-energy --username john --password secret123
  atmos-energy --username john --password secret123 --months 6
  atmos-energy --config ~/.atmos_energy/config.yaml
        """,
    )
    parser.add_argument('--username', '-u', help='Atmos Energy account username')
    parser.add_argument('--password', '-p', help='Atmos Energy account password')
    parser.add_argument(
        '--config',
        '-c',
        type=str,
        metavar='FILE',
        help='Configuration file (YAML format)',
    )
    parser.add_argument(
        '--months',
        type=int,
        default=1,
        metavar='N',
        help='Number of months to retrieve (default: 1 for current month only)',
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        metavar='FILE',
        help='Output to CSV file (default: print to console)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        logging.getLogger('atmos_energy').setLevel(logging.DEBUG)

    # Load config file if provided
    if args.config:
        try:
            config = load_config(args.config)
            args = merge_config(args, config)
            _LOGGER.debug('Loaded configuration from %s', args.config)
        except (FileNotFoundError, ValueError) as e:
            _LOGGER.error('Config error: %s', e)
            sys.exit(1)

    # Validate credentials
    if not args.username or not args.password:
        parser.error(
            'Username and password must be provided via --username/--password or --config'
        )

    # Initialize client
    client = AtmosEnergy(args.username, args.password)
    try:
        client.login()
        if args.months == 1:
            all_data = client.get_current_usage()
        else:
            all_data = client.get_usage_history(args.months)

        # Output data
        if args.output:
            write_csv(all_data, args.output)
        else:
            print_table(all_data)
    except Exception as e:  # pylint: disable=broad-except
        _LOGGER.error('Error retrieving usage data: %s', e)
        sys.exit(1)
    finally:
        client.logout()


if __name__ == '__main__':
    main()
