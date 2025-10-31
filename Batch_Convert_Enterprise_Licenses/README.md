# Meraki Bulk Update Network Feature Tier Script

This script is designed to convert the feature tier type of Meraki networks in an Subscription or Enterprise Agreement Subscription model-based Organization, it does this by using the Meraki Dashboard API batch operation. 

This script was written in mind for Organizations with an EA and many networks that needs to convert the feature tier from Essentials to Advantage for these networks on mass, however it works in either direction or it could be used as a single source of truth file for your feature tier to network assignments.

NOTE: As of 31st October 2025, this script is using an early access BETA API, as support for this endpoint in the Meraki Python Library is not yet available.

## Screenshots

![This is an example of before.](/Batch_Convert_Enterprise_Licenses/Before.png)
Before running the script
![This is an example of the script running.](/Batch_Convert_Enterprise_Licenses/Script_Running.png)
Running the script
![This is an example of after.](/Batch_Convert_Enterprise_Licenses/After.png)
After running the script

## Features

- Batch conversion of multiple networks using the `batchAdministeredLicensingSubscriptionNetworksFeatureTiersUpdate` API
- CSV file input for network data
- Network validation before conversion
- Comprehensive logging
- Retry logic for API calls
- Atomic operations (all succeed or all fail)

## Prerequisites

- Python 3.7 or higher
- Meraki Dashboard API key with appropriate permissions
- Access to Meraki networks you want to convert

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv e-2-a-env
   source e-2-a-env/bin/activate  # On Windows: e-2-a-env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### API Key Setup

Set your Meraki API key as an environment variable:
```bash
export MERAKI_API_KEY="your_api_key_here"
```

### CSV File Format

Create or update the included CSV file with the following format for what you want your networks to be:
```csv
network_id,product_type,feature_tier
N_1234567890,wireless,advantage
N_2345678901,switch,advantage
N_3456789012,appliance,advantage
```
i.e. N_3456789012 is an appliance network, and we want to be set with the advantage feature tier

**Required columns:**
- `network_id`: The Meraki network ID (e.g., N_1234567890)
- `product_type`: One of: wireless, switch, appliance, camera, sensor
- `feature_tier`: The target license tier (essentials, advantage)

## Usage

### Basic Usage

```bash
python meraki_license_converter.py
```

The script will:
1. Read network data from `networks.csv`
2. Validate that networks exist and are accessible
3. Create a batch operation payload
4. Execute the license conversion
5. Log results to both console and `meraki_conversion.log`

### Advanced Usage

You can customize the behaviour using environment variables:

```bash
# Use a different CSV file
export CSV_FILE_PATH="my_networks.csv"

# Skip network validation (faster but less safe)
export VALIDATE_NETWORKS="false"

# Allow partial success (non-atomic operation)
export IS_ATOMIC="false"

# Run the script
python meraki_license_converter.py
```


## API Reference

This script uses the Meraki Dashboard API endpoint:
- **Endpoint**: `POST /administered/licensing/subscription/networks/featureTiers/batchUpdate`
- **Documentation**: https://documentation.meraki.com/General_Administration/Licensing/Bulk_Update_Feature_Tier

### Batch Operation Payload

The script creates a payload in the following format:
```json
{
  "items": [
    {
      "network": {
        "id": "N_1234567890",
        "productTypes": [
          {
            "productType": "wireless",
            "featureTier": "advantage"
          }
        ]
      }
    }
  ],
  "isAtomic": true
}
```

## Logging

The script provides comprehensive logging:
- Console output for real-time monitoring
- Log file (`meraki_conversion.log`) for detailed records
- Different log levels: DEBUG, INFO, WARNING, ERROR

## Error Handling

The script includes robust error handling:
- Network validation before conversion
- Retry logic for API calls
- Graceful handling of missing or invalid data
- Detailed error messages and logging

## Security Considerations

- Store your API key securely (use environment variables)
- Ensure your API key has only the necessary permissions
- Review the CSV file before running to prevent unintended changes
- Test with a small subset of networks first

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your API key is set correctly and has the right permissions
2. **Network Not Found**: Verify network IDs in your CSV file
3. **Permission Denied**: Check that your API key has licensing administration permissions
4. **Rate Limiting**: The script includes retry logic, but you may need to wait if you hit rate limits


## License

This script is provided as-is for educational and operational purposes. Please ensure you have the necessary permissions and licenses before using it in production environments.

## Support

For issues related to:
- Meraki API: Check the [Meraki Developer Hub](https://developer.cisco.com/meraki/)
- This script: Review the logs and ensure all prerequisites are met
- This script is provided without support
- If required directly make the batch call with the Meraki API, if it is still failing contact Meraki Support