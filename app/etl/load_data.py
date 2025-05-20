import os
import pandas as pd
import logging
import glob
from sqlalchemy.orm import Session
from app.models import Earthquake
from app.data.utils import get_session

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def delete_old_records(session: Session, csv_file_path: str):
    """Delete old records with the same file_name."""
    try:
        # Create the delete query
        logger.info(f"Deleting old records from {csv_file_path}")
        deleted = (
            session.query(Earthquake)
            .filter(Earthquake.file_name == csv_file_path)
            .delete()
        )
        session.commit()
        logger.info(f"Deleted {deleted} old records")
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting old records: {e}")
        raise


def load_csv_to_postgres(session: Session, csv_file_path: str):
    """Load CSV data to PostgreSQL using SQLAlchemy."""
    try:
        logger.info(f"Loading data from {csv_file_path}")

        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Convert the DataFrame to a list of dictionaries
        earthquake_data = df.to_dict(orient="records")

        # Create Earthquake objects and add them to the session
        for record in earthquake_data:
            earthquake = Earthquake(**record)
            session.add(earthquake)

        # Commit the transaction
        session.commit()
        logger.info(f"Successfully loaded {len(earthquake_data)} records to database")
    except Exception as e:
        session.rollback()
        logger.error(f"Error loading data to PostgreSQL: {e}")
        raise


def find_latest_csv():
    """Find the latest earthquake data CSV file."""
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    csv_pattern = os.path.join(data_dir, "earthquake_data_*.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        logger.error("No earthquake data CSV files found")
        return None

    # Sort by modification time (newest first)
    latest_csv = max(csv_files, key=os.path.getmtime)
    logger.info(f"Found latest CSV file: {latest_csv}")
    return latest_csv


def main():
    """Main function to load earthquake data to PostgreSQL."""
    try:
        # Find the latest CSV file
        csv_file_path = find_latest_csv()
        if not csv_file_path:
            return

        # Get a database session
        session = get_session()

        try:
            # Delete old records with the same file_name
            delete_old_records(session, csv_file_path)

            # Load data from CSV to PostgreSQL
            load_csv_to_postgres(session, csv_file_path)

            logger.info("ETL process completed successfully")
        finally:
            session.close()
    except Exception as e:
        logger.error(f"An error occurred in the ETL process: {e}")


if __name__ == "__main__":
    main()
