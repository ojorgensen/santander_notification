#!/usr/bin/env python3
"""
Santander Cycle Station Notification App

This script checks the availability of empty docks at specified Santander Cycle
stations and sends email notifications when conditions are met.
"""

import os
from src.santander_notification.email_sender import send_notification_email
from src.santander_notification.tfl_cycle_data import (
    get_empty_docks,
    get_station_info,
    fetch_cycle_data,
    parse_cycle_data,
)


def check_station_and_notify(
    station_name="Westminster Pier, Westminster", empty_dock_threshold=5
):
    """
    Check a specific station for empty docks and send notification if the number
    of empty docks is below the threshold.

    Args:
        station_name (str): Name of the station to check
        empty_dock_threshold (int): Threshold for sending notification

    Returns:
        bool: True if notification was sent, False otherwise
    """
    # Get the number of empty docks at the station
    empty_docks, station_data = get_empty_docks(station_name)

    # If station not found
    if not station_data:
        print(f"Error: Station '{station_name}' not found.")
        return False

    # Check if the number of empty docks is below the threshold
    bikes_available = station_data.get("bikes_available", 0)
    total_docks = station_data.get("total_docks", 0)

    # Create a detailed message
    message = f"""
Santander Cycle Station Status Update for {station_name}:

Empty Docks: {empty_docks}
Bikes Available: {bikes_available}
Total Docks: {total_docks}

{"⚠️ WARNING: Low availability of empty docks!" if empty_docks <= empty_dock_threshold else "✅ Sufficient empty docks available."}
"""

    # Create the subject line
    subject = f"{'⚠️ ' if empty_docks <= empty_dock_threshold else ''}Santander Cycle Station Update: {station_name}"

    # Send email notification
    print(f"Sending notification for {station_name}:")
    print(message)

    return send_notification_email(subject, message)


def list_all_stations():
    """
    List all available Santander Cycle stations.
    Uses the TFL API to fetch and display all stations.
    """
    # Fetch the XML content directly
    xml_content = fetch_cycle_data()
    if not xml_content:
        print("Error: Could not fetch cycle station data.")
        return

    # Parse the XML to get all stations
    stations_dict = parse_cycle_data(xml_content)

    if not stations_dict:
        print("No stations found or error parsing data.")
        return

    stations_list = list(stations_dict.values())

    # First, print total count
    print(f"Found {len(stations_list)} stations")

    # Now let's search for Westminster stations
    westminster_stations = [
        s for s in stations_list if "westminster" in s.get("name", "Unknown").lower()
    ]

    # Display stations with "Westminster" in their name
    print("\nStations containing 'westminster':")
    for station in westminster_stations:
        print(
            f"- {station.get('name', 'Unknown')} (ID: {station.get('id', 'Unknown')})"
        )
        print(f"  Empty Docks: {station.get('empty_docks', 0)}")
        print(f"  Bikes Available: {station.get('bikes_available', 0)}")

    # Print a sample of station names (first 10)
    print("\nSample of station names:")
    for station in stations_list[:10]:
        print(
            f"- {station.get('name', 'Unknown')} (ID: {station.get('id', 'Unknown')})"
        )


if __name__ == "__main__":
    # Add this line to debug
    list_all_stations()

    # Default station to monitor - Westminster Pier
    default_station = "Westminster Pier, Westminster"

    # Get the station name from environment variable or use default
    station_name = os.getenv("CYCLE_STATION_NAME", default_station)

    # Get the threshold from environment variable or use default
    try:
        threshold = int(os.getenv("EMPTY_DOCK_THRESHOLD", "5"))
    except ValueError:
        threshold = 5

    # Check the station and send notification
    check_station_and_notify(station_name, threshold)
