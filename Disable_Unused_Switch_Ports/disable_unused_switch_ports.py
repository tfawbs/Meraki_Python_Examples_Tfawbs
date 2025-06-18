import meraki
import time
import os

# === USER VARIABLES ===
API_KEY = 'ENTER_YOUR_API_KEY_HERE'  # <-- Paste your Meraki API key here
TIMESPAN = 2678400  # 31 days in seconds
SERIALS_FILE = 'switch_serials.txt'  # File containing switch serials, one per line
# === END USER VARIABLES ===

def get_switch_serials(filename):
    if not os.path.exists(filename):
        print(f"Serials file '{filename}' not found.")
        return []
    with open(filename, 'r') as f:
        serials = [line.strip() for line in f if line.strip()]
    if not serials:
        print(f"No switch serials found in '{filename}'.")
    return serials

def process_switch(dashboard, serial):
    print(f"\nGetting switch port statuses for serial: {serial} (last 30 days)")
    try:
        port_statuses = dashboard.switch.getDeviceSwitchPortsStatuses(
            serial, timespan=TIMESPAN
        )
    except Exception as e:
        print(f"Error fetching port statuses for {serial}: {e}")
        return

    unused_ports = []
    for port in port_statuses:
        port_id = port.get('portId')
        usage = port.get('usageInKb', {})
        total_usage = usage.get('total', None)
        if total_usage == 0:
            unused_ports.append(port_id)

    if not unused_ports:
        print(f"No unused ports found to disable on {serial}.")
        return

    print(f"Found {len(unused_ports)} unused ports on {serial}: {unused_ports}")
    for port_id in unused_ports:
        try:
            print(f"Disabling port {port_id} on {serial}...")
            dashboard.switch.updateDeviceSwitchPort(
                serial,
                port_id,
                enabled=False
            )
            print(f"Port {port_id} on {serial} disabled.")
            time.sleep(0.5)  # Be gentle with the API
        except Exception as e:
            print(f"Failed to disable port {port_id} on {serial}: {e}")

def main():
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)
    serials = get_switch_serials(SERIALS_FILE)
    if not serials:
        return
    for serial in serials:
        process_switch(dashboard, serial)
    print("\nAll done.")

if __name__ == "__main__":
    main()