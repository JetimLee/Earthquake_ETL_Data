import os
import psycopg2
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def delete_old_records(conn, start_date, end_date):
    """Delete old records from the stage_earthquake table within a date range."""
    try:
        logger.info(f"Deleting old records between {start_date} and {end_date}")
        delete_query = """
            DELETE FROM stage_earthquakes 
            WHERE dt BETWEEN %s AND %s
        """
        cur = conn.cursor()
        # Convert date strings to datetime objects
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)
        cur.execute(delete_query, (start_datetime, end_datetime))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        logger.info(f"Deleted {deleted_count} old records")
    except Exception as e:
        logger.error(f"Error deleting old records: {e}")
        conn.rollback()
        raise


def transform_earthquake(conn, start_date, end_date):
    """Transform earthquake data and load it into the stage_earthquakes table using a different approach."""
    try:
        logger.info(f"Transforming earthquake data between {start_date} and {end_date}")
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)

        # First, let's fetch the earthquake data
        fetch_sql = """
            SELECT time, place, magnitude, latitude, longitude
            FROM earthquakes 
            WHERE to_timestamp(time / 1000) >= %s AND to_timestamp(time / 1000) <= %s
        """

        # Log the SQL query for debugging
        logger.info(f"Fetch SQL: {fetch_sql}")
        logger.info(f"Params: {start_datetime}, {end_datetime}")

        cur = conn.cursor()
        cur.execute(fetch_sql, (start_datetime, end_datetime))

        rows = cur.fetchall()
        logger.info(f"Fetched {len(rows)} earthquake records")

        # Now insert the transformed data one by one
        records_inserted = 0
        for row in rows:
            time, place, magnitude, latitude, longitude = row

            # Transform the data
            dt = datetime.fromtimestamp(time / 1000)

            # Extract region
            if " of " in place:
                region = place.split(" of ")[0].strip()
                location = place.split(" of ")[1].strip()
            elif "," in place:
                location = place.split(",")[0].strip()
                region = place.split(",")[-1].strip()
            else:
                region = "Unknown"
                location = place

            # Insert into stage table
            insert_sql = """
                INSERT INTO stage_earthquakes (dt, region, place, magnitude, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cur.execute(
                insert_sql, (dt, region, location, magnitude, latitude, longitude)
            )
            records_inserted += 1

        conn.commit()
        cur.close()

        logger.info(f"Transformed and loaded {records_inserted} records")
        return records_inserted
    except Exception as e:
        logger.error(f"Error in transform_earthquake: {e}")
        logger.error(f"Error type: {type(e)}")

        # Get more details about the error if available
        if hasattr(e, "__traceback__"):
            import traceback

            tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
            logger.error("Traceback: " + "".join(tb_lines))

        conn.rollback()
        raise


def calculate_date_range(days=15):
    """Calculate the date range for processing, defaulting to last 15 days."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date.isoformat(), end_date.isoformat()


def get_earthquake_stats(conn):
    """Get statistics on transformed earthquake data."""
    try:
        stats_sql = """
            SELECT 
                COUNT(*) as total_earthquakes,
                AVG(magnitude) as avg_magnitude,
                MAX(magnitude) as max_magnitude,
                MIN(dt) as earliest_date,
                MAX(dt) as latest_date,
                COUNT(DISTINCT region) as region_count
            FROM stage_earthquakes
        """
        cur = conn.cursor()
        cur.execute(stats_sql)
        result = cur.fetchone()
        cur.close()

        if result:
            total, avg_mag, max_mag, earliest, latest, region_count = result
            logger.info(f"Earthquake Statistics:")
            logger.info(f"  Total earthquakes: {total}")
            logger.info(f"  Average magnitude: {avg_mag:.2f}")
            logger.info(f"  Maximum magnitude: {max_mag:.2f}")
            logger.info(f"  Date range: {earliest} to {latest}")
            logger.info(f"  Regions affected: {region_count}")
    except Exception as e:
        logger.error(f"Error getting earthquake statistics: {e}")


def ensure_stage_table_exists(conn):
    """Ensure the stage_earthquakes table exists."""
    try:
        logger.info("Checking if stage_earthquakes table exists")
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS stage_earthquakes (
                id SERIAL PRIMARY KEY,
                dt TIMESTAMP,
                region VARCHAR(255),
                place VARCHAR(255),
                magnitude FLOAT,
                latitude FLOAT,
                longitude FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        logger.info("Stage table is ready")
    except Exception as e:
        logger.error(f"Error ensuring stage table exists: {e}")
        conn.rollback()
        raise


def main():
    """Main function to transform earthquake data."""
    try:
        # Database connection parameters
        db_params = {
            "dbname": os.getenv("DB_NAME", "earthquake_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASS", "postgres"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }

        # Calculate date range - default to last 15 days
        days_to_process = int(os.getenv("PROCESS_DAYS", "15"))
        start_date, end_date = calculate_date_range(days_to_process)

        logger.info(
            f"Starting earthquake data transformation for {start_date} to {end_date}"
        )

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)

        try:
            # Ensure stage table exists
            ensure_stage_table_exists(conn)

            # Delete old records in the date range
            delete_old_records(conn, start_date, end_date)

            # Transform and load data
            transformed_count = transform_earthquake(conn, start_date, end_date)

            # Get statistics on the transformed data
            if transformed_count > 0:
                get_earthquake_stats(conn)

            logger.info(
                f"Transformation completed successfully. Processed {transformed_count} records."
            )
        finally:
            conn.close()

    except Exception as e:
        logger.error(f"An error occurred during transformation: {e}")
        raise


if __name__ == "__main__":
    main()
