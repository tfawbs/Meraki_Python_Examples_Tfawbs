import meraki
import json
import os

# User should set these variables
API_KEY = "ENTER_YOUR_API_KEY_HERE"
ORGANIZATION_ID = "ENTER_YOUR_ORG_ID_HERE"

# Initialize Meraki client
dashboard = meraki.DashboardAPI(API_KEY)

# Step 1: Get all networks in the organization
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

# Step 2: Present network names to user for selection
print("Select a network to update:")
for idx, net in enumerate(networks):
    print(f"{idx + 1}: {net['name']} (ID: {net['id']})")

while True:
    try:
        selection = int(input("Enter the number of the network: "))
        if 1 <= selection <= len(networks):
            break
        else:
            print("Invalid selection. Try again.")
    except ValueError:
        print("Please enter a valid number.")

selected_network = networks[selection - 1]
network_id = selected_network['id']
network_name = selected_network['name']

# Step 3: Get existing L3 firewall rules
rules_response = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(network_id)
existing_rules = rules_response.get('rules', [])

# Remove the last rule (Default rule) if present
if existing_rules and existing_rules[-1].get('comment', '').lower() == 'default rule':
    existing_rules = existing_rules[:-1]

# Step 4: Save existing rules to a backup file
backup_filename = f"{network_id}.json"
with open(backup_filename, 'w') as backup_file:
    json.dump({"rules": existing_rules}, backup_file, indent=2)
print(f"Backed up existing rules to {backup_filename}")

# Step 5: Load standard rules from local file
standard_rules_path = os.path.join(os.path.dirname(__file__), 'standard-rules.json')
with open(standard_rules_path, 'r') as std_file:
    standard_rules_data = json.load(std_file)
standard_rules = standard_rules_data.get('rules', [])

# Step 6: Combine existing and standard rules (standard rules appended)
combined_rules = existing_rules + standard_rules

# Step 7: Upload combined rules to the network
update_body = {"rules": combined_rules}
dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(network_id, **update_body)
print(f"Uploaded combined rules to network '{network_name}' (ID: {network_id})") 