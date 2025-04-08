This script is setup to do the following

1. Get a list of all Network IDs in a configured OrgID
2. Scan all networks for their webhook configuration
2. Report the webhooks configured in an excel spreadsheet

## Screenshots

![This is an example of the output.](/Find_Configured_Webhooks/Screenshot.png)

## Requirements 

* python
* meraki
* openpyxl

To install run the command:
```
pip install meraki openpyxl
```

To run the script:
1. Update the script with any changes you want (ie extra outputs in the spreadsheet)
2. Fill in your API key and Org ID on lines 5 & 6
3. Run python3 main.py 

I would recommend running this in a virtual environment, see the Tips section in the top readme for more information.

For any troubleshooting I issues I would as always suggest Google is your friend and AI tools are excellent to build and troubleshoot with.