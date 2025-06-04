# Find Configured Webhooks Report

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

I recommend you run this in a Python Virtual Environment, if you're unfamiliar how to do that check out this [video](https://www.youtube.com/watch?v=Y21OR1OPC9A)

For any troubleshooting issues I would suggest Search Engines as the first point of call and using AI tools to assist work through and build out the script as they are excellent at troubleshooting and adding onto the existing script.

## Disclaimer

This script was built with AI assistance (GPT-4o), for the prompt I used see the ai_prompt.txt file. This script is provided with no warranty or support it is provided with the intent to be learnt from and built on. Please always follow best practices when engaging with the Meraki API, Python and any other coding tools.