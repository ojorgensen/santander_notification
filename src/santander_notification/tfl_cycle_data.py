import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple


def fetch_cycle_data(
    url: str = "https://tfl.gov.uk/tfl/syndication/feeds/cycle-hire/livecyclehireupdates.xml",
) -> Optional[str]:
    """
    Fetch the TfL cycle hire data from the specified URL.

    Args:
        url (str): The URL to fetch the data from

    Returns:
        Optional[str]: The XML content as a string or None if the request failed
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching TfL cycle data: {e}")
        return None


def parse_cycle_data(xml_content: str) -> Dict:
    """
    Parse the TfL cycle hire XML data.

    Args:
        xml_content (str): The XML content as a string

    Returns:
        Dict: A dictionary mapping station names to their information
    """
    if not xml_content:
        return {}

    try:
        root = ET.fromstring(xml_content)
        stations = {}

        # Extract station information
        for station in root:
            station_data = {
                "id": station.attrib.get("id", "unknown"),
                "name": "Unknown",
                "empty_docks": 0,
                "bikes_available": 0,
                "total_docks": 0,
                "latitude": 0,
                "longitude": 0,
            }

            # Extract all the station information from the XML
            for child in station:
                if child.tag == "name" and child.text:
                    station_data["name"] = child.text.strip()
                elif child.tag == "terminalName" and child.text:
                    station_data["terminal_name"] = child.text.strip()
                elif child.tag == "lat" and child.text:
                    try:
                        station_data["latitude"] = float(child.text.strip())
                    except ValueError:
                        pass
                elif child.tag == "long" and child.text:
                    try:
                        station_data["longitude"] = float(child.text.strip())
                    except ValueError:
                        pass
                elif child.tag == "nbEmptyDocks" and child.text:
                    try:
                        station_data["empty_docks"] = int(child.text.strip())
                    except ValueError:
                        pass
                elif child.tag == "nbBikes" and child.text:
                    try:
                        station_data["bikes_available"] = int(child.text.strip())
                    except ValueError:
                        pass
                elif child.tag == "nbDocks" and child.text:
                    try:
                        station_data["total_docks"] = int(child.text.strip())
                    except ValueError:
                        pass

            # Use a combination of station name and id as the key
            if station_data["name"] != "Unknown":
                stations[station_data["name"]] = station_data
            else:
                stations[station_data["id"]] = station_data

        # Print a debug message for the first station to understand its structure
        if stations:
            first_station = next(iter(stations.values()))
            print("DEBUG - First station data:")
            print(first_station)

        return stations
    except Exception as e:
        print(f"Error parsing TfL cycle data: {e}")
        return {}


def get_station_info(
    station_name: str = "Westminster Pier, Westminster",
) -> Optional[Dict]:
    """
    Get information for a specific station by name.

    Args:
        station_name (str): The name of the station to look for

    Returns:
        Optional[Dict]: Station information or None if the station was not found
    """
    xml_content = fetch_cycle_data()
    if not xml_content:
        return None

    stations = parse_cycle_data(xml_content)
    return stations.get(station_name)


def get_empty_docks(
    station_name: str = "Westminster Pier, Westminster",
) -> Tuple[int, Dict]:
    """
    Get the number of empty docks at a specific station.

    Args:
        station_name (str): The name of the station to look for

    Returns:
        Tuple[int, Dict]: The number of empty docks and the station data
    """
    station_data = get_station_info(station_name)

    if station_data:
        return station_data.get("empty_docks", 0), station_data
    else:
        return 0, {}


if __name__ == "__main__":
    # Test the module functionality
    station_name = "Westminster Pier, Westminster"
    empty_docks, station_data = get_empty_docks(station_name)

    if station_data:
        print(f"Station: {station_name}")
        print(f"Empty Docks: {empty_docks}")
        print(f"Bikes Available: {station_data.get('bikes_available', 0)}")
        print(f"Total Docks: {station_data.get('total_docks', 0)}")
        print(
            f"Location: {station_data.get('latitude', 0)}, {station_data.get('longitude', 0)}"
        )
    else:
        print(f"Station '{station_name}' not found.")
