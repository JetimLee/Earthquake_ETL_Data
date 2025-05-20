import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_earthquake_data():
    try:
        # Calculate date range
        today_date = datetime.now()
        fifteen_days_ago = today_date - timedelta(days=15)
        start_time = fifteen_days_ago.strftime("%Y-%m-%d")
        end_time = today_date.strftime("%Y-%m-%d")

        # Define API URL
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}"

        logger.info(f"Fetching earthquake data from {start_time} to {end_time}")

        # Make API request
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()
        logger.info(f"Received response with status code: {response.status_code}")

        # Process earthquake data
        earthquakes = []
        features = data.get("features", [])
        logger.info(f"Processing {len(features)} earthquake features")

        # Get the directory for saving the CSV
        # In Docker, this will be /app/data
        folder_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )

        # Create the directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        date = today_date.strftime("%Y_%m_%d")
        filename = os.path.join(folder_path, f"earthquake_data_{date}.csv")

        # Check if file already exists
        file_exists = os.path.isfile(filename)
        if file_exists:
            logger.info(f"File {filename} already exists and will be overwritten.")

        # Extract data from features
        for feature in features:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [0, 0, 0])

            earthquake = {
                "time": properties.get("time"),
                "place": properties.get("place"),
                "magnitude": properties.get("mag"),
                "longitude": coordinates[0] if len(coordinates) > 0 else 0,
                "latitude": coordinates[1] if len(coordinates) > 1 else 0,
                "depth": coordinates[2] if len(coordinates) > 2 else 0,
                "file_name": filename,
            }
            earthquakes.append(earthquake)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(earthquakes)
        df.to_csv(filename, index=False)

        logger.info(f"Data saved to {filename}")
        return filename

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching earthquake data: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    process_earthquake_data()
