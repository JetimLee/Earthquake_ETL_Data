import requests
import pandas as pd
from datetime import datetime, timedelta
import os


def process_earthquake_data():
    try:
        # Calculate date range
        today_date = datetime.now()
        fifteen_days_ago = today_date - timedelta(days=15)
        start_time = fifteen_days_ago.strftime("%Y-%m-%d")
        end_time = today_date.strftime("%Y-%m-%d")

        # Define API URL
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}"

        # Make API request
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()
        print(f"Status code: {response.status_code}")
        print(data)

        # Process earthquake data
        earthquakes = []
        features = data["features"]

        # Get the directory of the current script
        folder_path = os.path.dirname(os.path.abspath(__file__))
        date = today_date.strftime("%Y_%m_%d")
        filename = os.path.join(folder_path, f"earthquake_data_{date}.csv")

        # Check if file already exists
        file_exists = os.path.isfile(filename)
        if file_exists:
            print(f"File {filename} already exists and will be overwritten.")

        # Extract data from features
        for feature in features:
            properties = feature["properties"]
            geometry = feature["geometry"]
            earthquake = {
                "time": properties["time"],
                "place": properties["place"],
                "magnitude": properties["mag"],
                "longitude": geometry["coordinates"][0],
                "latitude": geometry["coordinates"][1],
                "depth": geometry["coordinates"][2],
                "file_name": filename,
            }
            earthquakes.append(earthquake)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(earthquakes)
        df.to_csv(filename, index=False)

        print(f"Data saved to {filename}")
        return filename

    except requests.exceptions.RequestException as e:
        print(f"Error fetching earthquake data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    process_earthquake_data()
