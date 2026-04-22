# Meraki Dynamic → Static Management IP Script

This script reads Meraki device serial numbers from a CSV file, looks up each device’s current `lanIp`, then updates the device’s management interface to use a **static** configuration with that IP.

It’s intended for cases where devices are currently set to “dynamic” management IP settings in Dashboard, but you want to pin them to their current IP address.

## Features

- **CSV input** of device serials
- **Uses current `lanIp`** from `getDevice` as the static IP
- **Sets static gateway, subnet mask, and DNS servers**
- **Dry run mode** to preview changes before applying
- **Helpful error output** on API failures

## Prerequisites

- Python 3.9+ (works with Python 3.12)
- A Meraki Dashboard API key with permission to read devices and update management interfaces

## Installation

Clone/download this folder, then create and activate a virtual environment:

```bash
python -m venv dynamic-2-static-env
source dynamic-2-static-env/bin/activate
```

Install the dependency:

```bash
pip install meraki
```

## Configuration

### API Key Setup

Set your API key as an environment variable:

```bash
export MERAKI_DASHBOARD_API_KEY="your_api_key_here"
```

### DNS & Gateway Updates

Set your DNS servers and Gateway IPs correctly on lines 39 and 50

### CSV File Format

You can use the included `serials_template.csv` as a starting point.

**Header format (recommended):**

```csv
serial
Q2XX-AAAA-BBBB
Q2XX-CCCC-DDDD
```

**No header format (also supported):**

```csv
Q2XX-AAAA-BBBB
Q2XX-CCCC-DDDD
```

If you use a different header name, pass `--serial-column`.

## Usage

### Dry run (recommended first)

```bash
python dynamic_to_static_meraki.py --csv serials_template.csv --dry-run
```

### Apply updates (real run)

```bash
python dynamic_to_static_meraki.py --csv serials_template.csv
```

### Common overrides

```bash
# Change gateway
python dynamic_to_static_meraki.py --csv serials_template.csv --gateway 192.168.20.1

# Change subnet mask (default is 255.255.255.0)
python dynamic_to_static_meraki.py --csv serials_template.csv --subnet-mask 255.255.254.0

# Override DNS servers (default is 192.168.20.2 and 8.8.8.8)
python dynamic_to_static_meraki.py --csv serials_template.csv --dns 192.168.20.2 8.8.8.8
```

## What the script changes

For each serial, the script:

1. Calls `getDevice(serial)` and reads `lanIp`
2. Calls `updateDeviceManagementInterface(serial, wan1=...)` with:
   - `usingStaticIp: true`
   - `staticIp: <current lanIp>`
   - `staticSubnetMask: <--subnet-mask>`
   - `staticGatewayIp: <--gateway>`
   - `staticDns: <--dns ...>`

## Troubleshooting

- **400 Bad Request**: Usually indicates a missing/invalid field in the payload (subnet mask/gateway/DNS), or the device/model/network doesn’t support the requested management interface change. The script prints the response details to help pinpoint the cause.
- **No `lanIp` returned**: The script will skip that device. Common causes are offline devices or devices that don’t report a LAN IP via that endpoint.
- **Permissions**: Make sure the API key has access to the org/network containing the serials.

## Security notes

- Prefer using the `MERAKI_DASHBOARD_API_KEY` environment variable instead of passing `--api-key` (to avoid leaking keys via shell history).
- Review your CSV carefully and always run with `--dry-run` first on a small set of devices.

