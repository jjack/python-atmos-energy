# CLI Usage

## Overview

The `atmos-energy` command-line tool allows you to retrieve Atmos Energy usage data without writing Python code.

## Basic Usage

### Get Current Month Usage

Display current month usage in the console:

```bash
atmos-energy --username user@example.com --password mypassword
```

**Note:** This makes **1 API request** to fetch the current billing period.

### Get Historical Data

Retrieve 6 months of usage data:

```bash
atmos-energy --username user@example.com --password mypassword --months 6
```

**Important:** This makes **6 API requests** (one per month). For performance-sensitive environments like Home Assistant, prefer `--months 1` for routine checks and use larger values only when historical analysis is needed.

### Export to CSV

Save usage data to a CSV file:

```bash
atmos-energy --username user@example.com --password mypassword --months 6 --output usage.csv
```

### Enable Verbose Logging

Show detailed debug information:

```bash
atmos-energy --username user@example.com --password mypassword --verbose
```

---

## Command-Line Options

```
usage: atmos-energy [-h] [--username USERNAME] [--password PASSWORD]
                    [--config FILE] [--months N] [--output FILE]
                    [--verbose]

Retrieve Atmos Energy usage data

options:
  -h, --help             Show this help message and exit
  --username, -u         Atmos Energy account username or email (required if no config)
  --password, -p         Atmos Energy account password (required if no config)
  --config, -c FILE      Path to YAML configuration file
  --months N             Number of months to retrieve (default: 1 for current month only)
                         ⚠️  Note: Each month requires 1 API request, so --months 6 makes 6 requests
  --output, -o FILE      Output to CSV file (default: print to console)
  --verbose, -v          Enable verbose logging
```

---

## Performance Considerations

### API Request Count

The `--months` parameter directly affects how many API requests are made:

| Months | API Requests | Best For |
|--------|--------------|----------|
| 1 (default) | 1 | Quick status checks, Home Assistant |
| 3 | 3 | Weekly reports |
| 6 | 6 | Monthly energy analysis |
| 12 | 12 | Annual reports (slower) |

### Recommendations

- **Home Assistant integrations:** Use default `--months 1` for routine updates
- **Daily checks:** Use `--months 1` to minimize API calls
- **Historical analysis:** Use larger values only when needed for reports
- **Rate limiting:** Be aware that 12 consecutive requests may take several seconds

### Example: Efficient Home Assistant Setup

```yaml
# config.yaml for regular Home Assistant polling
username: user@example.com
password: mypassword
months: 1  # Only current month - fast and minimal API calls
output: /data/atmos_energy/current.csv
```

---

## Configuration Files

### YAML Configuration

Store credentials and settings in a YAML file to avoid entering them on the command line:

```yaml
username: user@example.com
password: mypassword
months: 3
output: ~/usage_data.csv
```

### Using Configuration Files

Load settings from a configuration file:

```bash
atmos-energy --config ~/.atmos_energy/config.yaml
```

### Configuration File Priority

Command-line arguments override configuration file values:

```bash
# Uses config file's months setting (e.g., 3)
atmos-energy --config config.yaml

# Overrides config file's months setting with 6
atmos-energy --config config.yaml --months 6
```

### Recommended Setup

1. Create a configuration directory:
   ```bash
   mkdir -p ~/.atmos_energy
   ```

2. Create `~/.atmos_energy/config.yaml`:
   ```yaml
   username: user@example.com
   password: mypassword
   ```

3. Restrict permissions:
   ```bash
   chmod 600 ~/.atmos_energy/config.yaml
   ```

4. Run with config file:
   ```bash
   atmos-energy --config ~/.atmos_energy/config.yaml --months 6
   ```

---

## Output Formats

### Console Output (Default)

When no `--output` file is specified, usage data is printed to the console:

```
timestamp,value
2025-12-10T15:30:45,1.5
2025-12-11T15:30:45,2.0
2025-12-12T15:30:45,0.5
```

### CSV Output

Specify `--output` to save to a CSV file:

```bash
atmos-energy --username user@example.com --password mypassword --output usage.csv
```

The CSV file format is identical to console output:

```csv
timestamp,value
2025-12-10T15:30:45,1.5
2025-12-11T15:30:45,2.0
2025-12-12T15:30:45,0.5
```

---

## Examples

### Example 1: Quick Current Month Check

```bash
atmos-energy -u user@example.com -p mypassword
```

### Example 2: Full Year Export

```bash
atmos-energy --config ~/.atmos_energy/config.yaml --months 12 --output year_usage.csv
```

### Example 3: Debug Troubleshooting

```bash
atmos-energy --config ~/.atmos_energy/config.yaml --verbose
```

### Example 4: One-Time Query

```bash
atmos-energy --username user@example.com --password mypassword --months 3 --output temp_usage.csv
```

---

## Tips & Best Practices

1. **Use configuration files** for regular usage to avoid storing credentials in shell history
2. **Restrict file permissions** on config files: `chmod 600 ~/.atmos_energy/config.yaml`
3. **Use `--verbose`** if experiencing issues to see detailed debug information
4. **Redirect output** in scripts:
   ```bash
   atmos-energy --config config.yaml >> usage_log.csv
   ```

---

## Troubleshooting

### "Login failed" Error

- Verify your username and password are correct
- Check if your Atmos Energy account is active
- Try `--verbose` for more details

### No Data Returned

- Verify you have usage data available for the requested period
- Try `--verbose` to see API responses
- Try with `--months 1` first to see if current month data is available

### File Permission Errors

Ensure your output directory is writable:

```bash
mkdir -p ~/energy_data
atmos-energy --config config.yaml --output ~/energy_data/usage.csv
```
