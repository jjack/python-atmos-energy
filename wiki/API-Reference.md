# API Reference

## AtmosEnergy Class

The main client class for interacting with the Atmos Energy Account Center API.

### `__init__(username: str, password: str)`

Initialize the client with your Atmos Energy credentials.

**Args:**
- `username` (str): Your Atmos Energy account username or email
- `password` (str): Your Atmos Energy account password

**Example:**
```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')
```

---

## Methods

### `login() -> None`

Authenticate with the Atmos Energy Account Center.

This method must be called before calling `get_usage()`. It retrieves the form ID required for subsequent API calls and establishes an authenticated session.

**Raises:**
- `Exception`: If login fails or form ID cannot be found

**Example:**
```python
try:
    client.login()
except Exception as e:
    print(f"Login failed: {e}")
```

---

### `get_usage() -> list[tuple[int, float]]`

Retrieve usage data for the current billing period.

Makes a **single API request** to retrieve the current month's usage data.

**Returns:**
- `list[tuple[int, float]]`: A list of (timestamp, value) tuples where:
  - `timestamp` (int): Unix timestamp (seconds since epoch)
  - `value` (float): Energy usage reading (in the unit reported by Atmos Energy)

**Raises:**
- `Exception`: If content type is invalid or workbook parsing fails

**Example:**
```python
# Get current month usage (1 API request)
current = client.get_usage()

for timestamp, usage in current:
    print(f"Usage: {usage} at {timestamp}")
```

---

### `get_usage_history(months: int) -> list[tuple[int, float]]`

Retrieve historical usage data for multiple billing periods.

Makes **multiple API requests** (one per billing period) to retrieve historical usage data for the specified number of months.

**Args:**
- `months` (int): Number of billing periods to retrieve (e.g., 6 for 6 months)

**Returns:**
- `list[tuple[int, float]]`: A list of (timestamp, value) tuples aggregated across all requested periods where:
  - `timestamp` (int): Unix timestamp (seconds since epoch)
  - `value` (float): Energy usage reading (in the unit reported by Atmos Energy)

**Raises:**
- `Exception`: If content type is invalid or workbook parsing fails

**Example:**
```python
# Get 6 months of historical data (6 API requests)
historical = client.get_usage_history(months=6)

# Process the aggregated data
for timestamp, usage in historical:
    print(f"Usage: {usage} at {timestamp}")
```

---

### When to Use Each Method

| Method | Use Case | Requests |
|--------|----------|----------|
| `get_usage()` | Get current month's data | 1 |
| `get_usage_history(months=1)` | Explicitly request single month as history | 1 |
| `get_usage_history(months=6)` | Get 6 months of historical data | 6 |
| `get_usage_history(months=12)` | Get 1 year of historical data | 12 |

**Note:** The distinction between methods is intentional to make the number of API requests transparent to the caller. This is important for performance considerations, especially in Home Assistant integrations.

---

### `logout() -> None`

Log out and close the session.

This should be called when done to properly close the authenticated session.

**Example:**
```python
try:
    client.login()
    usage = client.get_usage()
    # Process usage...
finally:
    client.logout()  # Ensure logout even if an error occurs
```

---

## Usage Patterns

### Get Current Month Usage (Single Request)

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    client.login()
    
    # Get current month (1 API request)
    usage_data = client.get_usage()
    
    for timestamp, value in usage_data:
        print(f"Timestamp: {timestamp}, Usage: {value}")
        
finally:
    client.logout()
```

### Get Historical Data (Multiple Requests)

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    client.login()
    
    # Get 6 months of historical data (6 API requests)
    usage_data = client.get_usage_history(months=6)
    
    for timestamp, value in usage_data:
        print(f"Timestamp: {timestamp}, Usage: {value}")
        
finally:
    client.logout()
```

### Error Handling Pattern

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    client.login()
    
    # Get usage data
    usage = client.get_usage_history(months=3)
    
    # Process the data
    total_usage = sum(value for _, value in usage)
    print(f"Total usage: {total_usage}")
    
except Exception as e:
    print(f"Error retrieving usage data: {e}")
    
finally:
    try:
        client.logout()
    except Exception as e:
        print(f"Error during logout: {e}")
```

### Performance Consideration for Home Assistant

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    client.login()
    
    # For Home Assistant, prefer get_usage() for minimal API calls
    # when only current month is needed
    current_usage = client.get_usage()  # Fast: 1 API request
    
    # Use get_usage_history() only when historical data is needed
    # Remember: months=12 makes 12 API requests
    historical_usage = client.get_usage_history(months=12)  # Slow: 12 API requests
    
finally:
    client.logout()
```

---

## Data Structure

### Usage Data Format

`get_usage()` returns a list of tuples:

```python
[
    (1702200000, 1.5),   # timestamp, usage_value
    (1702286400, 2.0),
    (1702372800, 0.5),
]
```

- **timestamp** (int): Unix timestamp representing the end of the billing period
- **value** (float): The usage reading for that billing period

### Converting Timestamps

To convert Unix timestamps to human-readable dates:

```python
from datetime import datetime

timestamp = 1702200000
readable_date = datetime.fromtimestamp(timestamp)
print(readable_date)  # 2023-12-10 16:00:00
```

---

## Notes

- Credentials are never stored; they're only used for the session
- Sessions expire after periods of inactivity
- The `months` parameter refers to billing periods, not calendar months
- Usage data is provided by Atmos Energy and typically includes daily or monthly readings depending on your billing cycle
