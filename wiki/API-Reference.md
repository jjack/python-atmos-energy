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

### `get_usage(months: int = 1) -> list[tuple[int, float]]`

Retrieve usage data for the specified number of billing periods.

**Args:**
- `months` (int, optional): Number of billing periods to retrieve. Default is 1 (current month).

**Returns:**
- `list[tuple[int, float]]`: A list of (timestamp, value) tuples where:
  - `timestamp` (int): Unix timestamp (seconds since epoch)
  - `value` (float): Energy usage reading (in the unit reported by Atmos Energy)

**Raises:**
- `Exception`: If content type is invalid or workbook parsing fails

**Example:**
```python
# Get current month usage
current = client.get_usage()

# Get 6 months of historical data
historical = client.get_usage(months=6)

# Process the data
for timestamp, usage in historical:
    print(f"Usage: {usage} at {timestamp}")
```

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

## Usage Pattern

### Basic Pattern

```python
from atmos_energy import AtmosEnergy

# Create client
client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    # Login
    client.login()
    
    # Get usage data
    usage_data = client.get_usage(months=3)
    
    # Process the data
    for timestamp, value in usage_data:
        print(f"Timestamp: {timestamp}, Usage: {value}")
        
finally:
    # Always logout
    client.logout()
```

### Error Handling

```python
from atmos_energy import AtmosEnergy

client = AtmosEnergy(username='user@example.com', password='mypassword')

try:
    client.login()
    usage = client.get_usage(months=6)
    
except Exception as e:
    print(f"Error retrieving usage data: {e}")
    
finally:
    try:
        client.logout()
    except Exception as e:
        print(f"Error during logout: {e}")
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
