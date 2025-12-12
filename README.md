# Atmos Energy Client

A Python client library for retrieving energy usage data from the Atmos Energy Account Center. Primarily intended for use with the [Home Assistant Atmos Energy Addon](https://github.com/jjack/hass-atmos-energy) or the [Home Assistant Import Energy Data Project](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data)

## Features

- Secure authentication with Atmos Energy Account Center
- Retrieve current and historical usage data
- YAML configuration file support
- CSV export functionality

## Installation

```bash
pip install atmos-energy
```

## Quick Start

### CLI

```bash
atmos-energy --username user@example.com --password mypassword
```

### Python API

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')
client.login()
usage = client.get_usage(months=6)  # Get 6 months of data
client.logout()
```

## Documentation

- **[API Reference](https://github.com/jjack/python-atmos-energy/wiki/API-Reference)** - Detailed API documentation
- **[CLI Usage](https://github.com/jjack/python-atmos-energy/wiki/CLI-Usage)** - Command-line options and configuration files
- **[Data Formats](https://github.com/jjack/python-atmos-energy/wiki/Data-Formats)** - Usage data and CSV output formats
- **[Development](https://github.com/jjack/python-atmos-energy/wiki/Development)** - Setup, testing, and code quality

## License

Apache 2.0 License - see [LICENSE](https://github.com/jjack/python-atmos-energy/blob/main/LICENSE) for details

## Contributing

Contributions are welcome! Please open a [GitHub Issue](https://github.com/jjack/python-atmos-energy/issues) or submit a [Pull Request](https://github.com/jjack/python-atmos-energy/pulls).

## Disclaimer

This project is not affiliated with or endorsed by [Atmos Energy](https://www.atmosenergy.com/) and comes with no warranties. Use at your own risk.
