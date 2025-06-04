import meraki
import openpyxl

# Define your Meraki API Key and Organization ID
API_KEY = "MY_API_KEY_HERE"
ORGANIZATION_ID = "MY_ORG_ID_HERE"

# Initialize Meraki client
dashboard = meraki.DashboardAPI(API_KEY, caller='PythonExamples/1.0 TFawbs')

# Create a workbook and select the active worksheet
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Webhook Servers"

# Define the header
sheet.append(["Network Name", "Network ID", "Webhook Name", "Webhook URL"])

# Fetch all networks in the organization
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

for network in networks:
    network_id = network['id']
    network_name = network['name']
    
    # Fetch all webhook HTTP servers for the network
    webhooks = dashboard.networks.getNetworkWebhooksHttpServers(network_id)
    
    for webhook in webhooks:
        webhook_name = webhook['name']
        webhook_url = webhook['url']
        
        # Append data to the Excel sheet
        sheet.append([network_name, network_id, webhook_name, webhook_url])

# Save the workbook
workbook.save("webhook_servers.xlsx")

print("Data has been successfully written to webhook_servers.xlsx")