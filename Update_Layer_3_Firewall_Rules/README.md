This script is designed to allow you to add Layer 3 firewall rules to a network from a JSON file which contains a set of standard rules or templated rules you want applied everywhere.

For example, consider this as a use case, you need to roll out a new set of L3 firewall rules to many Meraki Networks for a new app or service deployment, this takes time at scale and can result in human error making it a problem at the click-ops level.

The script allows you to configure these rules one time in the standard-rules.json file. Running the script will add these rules to the existing Layer 3 rules in a network you specify without overwriting any existing rules!

It does this by taking the following steps:
1. Get a list of all Network IDs in a the OrgID
2. Ask the user which network to target (Listed by name in the terminal)
3. Get a list of the existing Layer 3 Firewall rules for that network
4. Omit the Default Any Any Outbound Rule from this list
5. Save this list as a backup to a file called networkId.json
6. Load in the rules from the standard-rules.json file
7. Combine the existing rules with the standards rules
8. Lastly upload the combined list to the network

If you have no existing rules that doesn't impact the script at all. It still applies the rules from standard-rules.json to the network, so you could run the script to push out rules to new sites even.

## Screenshots

![This is an example of before.](/Update_Layer_3_Firewall_Rules/Before.png)
Before running the script
![This is an example of after.](/Update_Layer_3_Firewall_Rules/After.png)
After running the script

## Requirements 

* python
* meraki

To install run the command:
```
pip install meraki 
```

To run the script:
1. Update with your API key and Org ID on lines 6 & 7
2. Update the standard-rules.json file with your standard set of Layer 3 firewall rules
3. Run python3 update_l3_firewall_rules.py

I recommend you run this in a Python Virtual Environment, if you're unfamiliar how to do that check out this [video](https://www.youtube.com/watch?v=Y21OR1OPC9A)

For any troubleshooting issues I would suggest Search Engines as the first point of call and using AI tools to assist work through and build out the script as they are excellent at troubleshooting and adding onto the existing script.

## Disclaimer

This script was built with AI assistance (GPT-4o), for the prompt I used see the ai_prompt.txt file. This script is provided with no warranty or support it is provided with the intent to be learnt from and built on. Please always follow best practices when engaging with the Meraki API, Python and any other coding tools.