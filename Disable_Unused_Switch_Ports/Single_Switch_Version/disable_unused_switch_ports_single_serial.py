import meraki
import time

# === USER VARIABLES ===
API_KEY = 'ENTER_YOUR_API_KEY_HERE'  # <-- Paste your Meraki API key here
SWITCH_SERIAL = 'Q2MW-AAAA-1234'  # <-- Paste your switch serial here
TIMESPAN = 2678400  # 31 days in seconds

# === END USER VARIABLES ===

def main():
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    print(f"Getting switch port statuses for serial: {SWITCH_SERIAL} (last 30 days)")
    try:
        port_statuses = dashboard.switch.getDeviceSwitchPortsStatuses(
            SWITCH_SERIAL, timespan=TIMESPAN
        )
    except Exception as e:
        print(f"Error fetching port statuses: {e}")
        return

    unused_ports = []
    for port in port_statuses:
        port_id = port.get('portId')
        usage = port.get('usageInKb', {})
        total_usage = usage.get('total', None)
        if total_usage == 0:
            unused_ports.append(port_id)

    if not unused_ports:
        print("No unused ports found to disable.")
        return

    print(f"Found {len(unused_ports)} unused ports: {unused_ports}")
    for port_id in unused_ports:
        try:
            print(f"Disabling port {port_id}...")
            dashboard.switch.updateDeviceSwitchPort(
                SWITCH_SERIAL,
                port_id,
                enabled=False
            )
            print(f"Port {port_id} disabled.")
            time.sleep(0.5)  # Be gentle with the API
        except Exception as e:
            print(f"Failed to disable port {port_id}: {e}")

    print("Done.")

if __name__ == "__main__":
    main() 