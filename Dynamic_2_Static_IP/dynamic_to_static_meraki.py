#!/usr/bin/env python3
"""
Set Meraki devices from dynamic to static management IP settings.

Workflow:
1. Read target serial numbers from a CSV file.
2. Use getDevice to retrieve current LAN IP per serial.
3. Push static management interface settings with updateDeviceManagementInterface.
"""

import argparse
import csv
import os
import sys
from typing import Iterable, List

import meraki


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read Meraki serial numbers from CSV and set static management "
            "IP configuration using current LAN IP."
        )
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file containing serial numbers.",
    )
    parser.add_argument(
        "--serial-column",
        default="serial",
        help="CSV column name for serial numbers (default: serial).",
    )
    parser.add_argument(
        "--gateway",
        default="192.168.20.1",
        help="Static gateway IP to apply (default: 192.168.20.1).",
    )
    parser.add_argument(
        "--subnet-mask",
        default="255.255.255.0",
        help="Static subnet mask to apply (default: 255.255.255.0).",
    )
    parser.add_argument(
        "--dns",
        nargs="+",
        default=["192.168.20.2", "8.8.8.8"],
        help="One or more DNS servers to apply (default: 192.168.20.2 8.8.8.8).",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("MERAKI_DASHBOARD_API_KEY"),
        help=(
            "Meraki API key. If omitted, reads MERAKI_DASHBOARD_API_KEY "
            "environment variable."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended changes without updating Dashboard.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose SDK logging to stdout.",
    )
    return parser.parse_args()


def _csv_delimiter(sample: str) -> str:
    """Pick a delimiter; comma default when the sniffer cannot decide (e.g. one column, no commas)."""
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;").delimiter
    except csv.Error:
        return ","


def _first_nonempty_line(sample: str) -> str:
    for line in sample.splitlines():
        if line.strip():
            return line
    return ""


def _split_csv_row(line: str, delimiter: str) -> List[str]:
    try:
        return next(csv.reader([line], delimiter=delimiter))
    except StopIteration:
        return []


def _first_row_declares_serial_column(
    first_line: str, delimiter: str, serial_column: str
) -> bool:
    cells = [cell.strip() for cell in _split_csv_row(first_line, delimiter)]
    return serial_column in cells


def read_serials(csv_path: str, serial_column: str) -> List[str]:
    serials: List[str] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(2048)
        handle.seek(0)
        delimiter = _csv_delimiter(sample)
        first_line = _first_nonempty_line(sample)
        has_header = _first_row_declares_serial_column(
            first_line, delimiter, serial_column
        )

        if has_header:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                raise ValueError("CSV header could not be read.")
            if serial_column not in reader.fieldnames:
                raise ValueError(
                    f"CSV is missing '{serial_column}' column. "
                    f"Found: {reader.fieldnames}"
                )
            for row in reader:
                serial = (row.get(serial_column) or "").strip()
                if serial:
                    serials.append(serial)
        else:
            reader = csv.reader(handle, delimiter=delimiter)
            for row in reader:
                if not row:
                    continue
                serial = (row[0] or "").strip()
                if serial:
                    serials.append(serial)

    # Preserve order, remove duplicates.
    unique_serials = list(dict.fromkeys(serials))
    return unique_serials


def chunked(items: Iterable[str], size: int = 1) -> Iterable[List[str]]:
    batch: List[str] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def main() -> int:
    args = parse_args()

    if not args.api_key:
        print(
            "ERROR: API key not provided. Set MERAKI_DASHBOARD_API_KEY or use --api-key.",
            file=sys.stderr,
        )
        return 1

    try:
        serials = read_serials(args.csv, args.serial_column)
    except Exception as exc:
        print(f"ERROR: Failed to parse CSV '{args.csv}': {exc}", file=sys.stderr)
        return 1

    if not serials:
        print("No serial numbers found in CSV. Nothing to do.")
        return 0

    dashboard = meraki.DashboardAPI(
        api_key=args.api_key,
        print_console=args.verbose,
        suppress_logging=not args.verbose,
    )

    success = 0
    skipped = 0
    failed = 0

    print(f"Loaded {len(serials)} serial(s). Starting updates...")
    for serial in serials:
        try:
            device = dashboard.devices.getDevice(serial)
            lan_ip = device.get("lanIp")

            if not lan_ip:
                skipped += 1
                print(f"[SKIP] {serial}: No lanIp returned by getDevice.")
                continue

            payload = {
                "wan1": {
                    "usingStaticIp": True,
                    "staticIp": lan_ip,
                    "staticSubnetMask": args.subnet_mask,
                    "staticGatewayIp": args.gateway,
                    "staticDns": args.dns,
                }
            }

            if args.dry_run:
                print(f"[DRY-RUN] {serial}: would apply {payload}")
                success += 1
                continue

            dashboard.devices.updateDeviceManagementInterface(serial, **payload)
            success += 1
            print(
                f"[OK] {serial}: staticIp={lan_ip}, mask={args.subnet_mask}, "
                f"gateway={args.gateway}, dns={args.dns}"
            )

        except meraki.APIError as api_error:
            failed += 1
            details = ""
            if getattr(api_error, "message", None):
                details = f" | {api_error.message}"
            elif getattr(api_error, "response", None) is not None:
                try:
                    details = f" | {api_error.response.text}"
                except Exception:
                    details = ""
            print(
                f"[FAIL] {serial}: API error {api_error.status} - {api_error.reason}{details}",
                file=sys.stderr,
            )
        except Exception as exc:
            failed += 1
            print(f"[FAIL] {serial}: {exc}", file=sys.stderr)

    print("\nCompleted.")
    print(f"  Success: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
