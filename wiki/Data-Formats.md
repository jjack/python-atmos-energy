# Data Formats

## Usage Data Structure

### Python API Return Format

The `get_current_usage()` method returns a list of tuples:

```python
[
    (1702200000, 1.5),
    (1702286400, 2.0),
    (1702372800, 0.5),
]
```

Each tuple contains:
- **timestamp** (int): Unix timestamp in seconds (UTC)
- **value** (float): Energy usage reading

### Timestamp Reference

Unix timestamps represent seconds since January 1, 1970, 00:00:00 UTC.

#### Converting to Readable Dates

**Python:**
```python
from datetime import datetime

timestamp = 1702200000
readable = datetime.fromtimestamp(timestamp)
print(readable)  # 2023-12-10 16:00:00
```

**ISO 8601 Format:**
```python
from datetime import datetime

timestamp = 1702200000
iso_format = datetime.utcfromtimestamp(timestamp).isoformat()
print(iso_format)  # 2023-12-10T16:00:00
```

---

## CSV Output Format

### File Structure

When using `--output` with the CLI or processing CSV exports:

```csv
timestamp,value
2025-12-10T15:30:45,1.5
2025-12-11T15:30:45,2.0
2025-12-12T15:30:45,0.5
2025-12-13T15:30:45,0.8
```

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | String (ISO 8601) | End of billing period in ISO format (YYYY-MM-DDTHH:MM:SS) |
| `value` | Float | Energy usage reading |

### CSV Examples

#### 30 Days of Data
```csv
timestamp,value
2025-11-11T15:30:45,1.2
2025-11-12T15:30:45,1.5
2025-11-13T15:30:45,0.9
2025-11-14T15:30:45,2.1
2025-11-15T15:30:45,1.8
```

#### Import into Excel/Sheets

Most spreadsheet applications can directly import CSV files:

1. **Excel**: File → Open → Select CSV file
2. **Google Sheets**: File → Import → Upload → Select CSV file
3. **LibreOffice Calc**: File → Open → Select CSV file

---

## Data Interpretation

### Understanding Your Usage Data

- **Timestamp**: Represents when the billing period ended
- **Value**: The usage reading for that billing period (typically in kWh for electricity)

### Billing Period Calculation

The `--months` parameter retrieves the last N complete billing periods:

```bash
atmos-energy --months 1   # Current/most recent month
atmos-energy --months 3   # Last 3 months
atmos-energy --months 12  # Last 12 months
```

### Data Availability

- Most recent data: Usually available within 1-2 days after billing period end
- Historical data: Available for several years back
- Gaps: May occur if service was interrupted or account was inactive

---

## Working with Usage Data

### Processing in Python

```python
from atmos_energy import AtmosEnergy
from datetime import datetime

client = AtmosEnergy(username='user@example.com', password='mypassword')
client.login()

usage_data = client.get_current_usage(months=12)

# Calculate total usage
total = sum(value for _, value in usage_data)
print(f"Total yearly usage: {total} kWh")

# Find peak usage
peak_usage, peak_timestamp = max(usage_data, key=lambda x: x[1])
print(f"Peak usage: {peak_usage} kWh on {datetime.fromtimestamp(peak_timestamp)}")

# Find lowest usage
min_usage, min_timestamp = min(usage_data, key=lambda x: x[1])
print(f"Lowest usage: {min_usage} kWh on {datetime.fromtimestamp(min_timestamp)}")

# Calculate average
average = total / len(usage_data)
print(f"Average usage: {average:.2f} kWh")

client.logout()
```

### Exporting to Different Formats

#### JSON Export
```python
import json
from datetime import datetime
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')
client.login()
usage_data = client.get_current_usage(months=6)

# Convert to JSON-friendly format
data = [
    {
        'timestamp': datetime.fromtimestamp(ts).isoformat(),
        'value': value
    }
    for ts, value in usage_data
]

with open('usage.json', 'w') as f:
    json.dump(data, f, indent=2)

client.logout()
```

#### Pandas DataFrame
```python
import pandas as pd
from datetime import datetime
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')
client.login()
usage_data = client.get_current_usage(months=12)

# Create DataFrame
df = pd.DataFrame(
    [(datetime.fromtimestamp(ts), value) for ts, value in usage_data],
    columns=['timestamp', 'value']
)

# Save to CSV
df.to_csv('usage_data.csv', index=False)

# Basic statistics
print(df.describe())

client.logout()
```

---

## Typical Usage Patterns

### Residential Usage

Typical residential usage varies by region, season, and usage habits:

- **Summer Peak**: Higher due to air conditioning (1.5-3.0 kWh/day typical)
- **Winter Peak**: Higher due to heating (1.0-2.5 kWh/day typical)
- **Shoulder Seasons**: Lower usage (0.5-1.5 kWh/day typical)

### Data Quality

- **Missing Data**: May indicate service interruptions or account issues
- **Sudden Spikes**: May indicate appliance issues or unusual usage
- **Flat Periods**: May indicate meters not reporting or service issues

---

## Units

The library returns usage data in the units provided by Atmos Energy. Typically:

- **Electricity**: Kilowatt-hours (kWh)
- **Natural Gas**: Therms or cubic feet

Verify your utility bill to confirm the units for your account.

---

## Limitations

- Data is provided as-is from Atmos Energy servers
- Billing periods vary by account (typically monthly)
- Historical data retention depends on Atmos Energy's data storage policies
- Real-time data is not available; data lags by 1-2 days typically
