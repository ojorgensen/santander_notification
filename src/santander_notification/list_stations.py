#!/usr/bin/env python3
"""
TfL Cycle Station Listing Tool

This script fetches and lists all available TfL Santander Cycle stations
to help users find the exact name of the station they want to monitor.
"""

from tfl_cycle_data import fetch_cycle_data, parse_cycle_data


def list_all_stations(search_term=None):
    """
    Fetch and list all available TfL Santander Cycle stations.
    Optionally filter by a search term.

    Args:
        search_term (str, optional): Filter stations by this term
    """
    print("Fetching TfL Santander Cycle stations data...")
    xml_content = fetch_cycle_data()

    if not xml_content:
        print("Error: Failed to fetch TfL cycle data.")
        return

    stations = parse_cycle_data(xml_content)

    if not stations:
        print("Error: No stations found or failed to parse station data.")
        return

    # Filter stations if search term provided
    if search_term:
        search_term = search_term.lower()
        filtered_stations = {
            name: data for name, data in stations.items() if search_term in name.lower()
        }
        if not filtered_stations:
            print(f"No stations found matching '{search_term}'.")
            print("Showing all stations instead.")
            filtered_stations = stations
    else:
        filtered_stations = stations

    # Print station information
    print(f"\nFound {len(filtered_stations)} stations:")
    print("-" * 80)

    for i, (name, data) in enumerate(sorted(filtered_stations.items()), 1):
        empty_docks = data.get("empty_docks", 0)
        bikes = data.get("bikes_available", 0)
        total = data.get("total_docks", 0)

        print(f"{i}. {name}")
        print(f"   Empty Docks: {empty_docks}, Bikes: {bikes}, Total: {total}")
        print(f"   ID: {data.get('id', 'unknown')}")
        print("-" * 80)

    print(
        "\nTo monitor a station, set the CYCLE_STATION_NAME in your .env file to the exact station name."
    )
    print("Example: CYCLE_STATION_NAME=Westminster Pier, Westminster")


if __name__ == "__main__":
    import sys

    search_term = None
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
        print(f"Searching for stations matching: '{search_term}'")

    list_all_stations(search_term)
