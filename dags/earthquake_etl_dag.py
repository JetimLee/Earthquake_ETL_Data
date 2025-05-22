from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "earthquake_etl_pipeline_with_viz",
    default_args=default_args,
    description="ETL pipeline for earthquake data with visualization",
    schedule_interval=timedelta(days=1),  # Run once a day
    start_date=days_ago(1),  # Start running from yesterday
    catchup=False,  # Don't run for the past dates
    tags=["etl", "earthquake", "visualization"],
)

# Run database migrations
run_migrations = BashOperator(
    task_id="run_migrations",
    bash_command="cd /opt/airflow && python -m alembic upgrade head",
    dag=dag,
)

# Define ETL steps using BashOperator to execute Python scripts
extract_task = BashOperator(
    task_id="extract_earthquake_data",
    bash_command="cd /opt/airflow && python -m app.etl.process_earthquake_data",
    dag=dag,
)

load_task = BashOperator(
    task_id="load_data_to_db",
    bash_command="cd /opt/airflow && python -m app.etl.load_data",
    dag=dag,
)

transform_task = BashOperator(
    task_id="transform_data",
    bash_command="cd /opt/airflow && python -m app.etl.transform_data",
    dag=dag,
)


# Add visualization task
def generate_earthquake_visualizations():
    """Generate visualizations for earthquake data."""
    import pandas as pd
    import os
    import sys
    from datetime import datetime

    # Create directory and initialize logging
    viz_dir = "/opt/airflow/data/visualizations"
    os.makedirs(viz_dir, exist_ok=True)

    def log_debug(message):
        print(message)  # For Airflow logs
        with open(f"{viz_dir}/viz_debug.log", "a") as f:
            f.write(f"{datetime.now()}: {message}\n")

    log_debug("Starting visualization generation")

    try:
        # Import required libraries
        log_debug("Importing visualization libraries")
        import matplotlib

        matplotlib.use("Agg")  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import numpy as np

        log_debug(f"Using matplotlib version: {matplotlib.__version__}")

        log_debug("Importing folium")
        import folium
        from folium.plugins import HeatMap, MarkerCluster, MeasureControl

        # Connect to database
        log_debug("Connecting to database")
        import psycopg2

        db_params = {
            "dbname": os.getenv("DB_NAME", "earthquake_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASS", "postgres"),
            "host": os.getenv("DB_HOST", "postgres"),
            "port": os.getenv("DB_PORT", "5432"),
        }
        log_debug(f"Database parameters: {db_params}")

        conn = psycopg2.connect(**db_params)
        log_debug("Successfully connected to database")

        # Query data - limit to 500 for performance
        query = """
        SELECT dt, region, place, magnitude, latitude, longitude, depth
        FROM stage_earthquakes
        ORDER BY dt DESC
        LIMIT 500
        """

        log_debug("Executing query")
        df = pd.read_sql(query, conn)
        conn.close()
        log_debug(f"Retrieved {len(df)} earthquake records")

        # 1. Create enhanced magnitude distribution histogram
        log_debug("Creating magnitude histogram")
        plt.figure(figsize=(10, 6))
        bins = np.linspace(df["magnitude"].min(), df["magnitude"].max(), 20)
        plt.hist(
            df["magnitude"], bins=bins, color="skyblue", edgecolor="black", alpha=0.7
        )
        plt.title("Earthquake Magnitude Distribution", fontsize=16)
        plt.xlabel("Magnitude", fontsize=14)
        plt.ylabel("Frequency", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle="--")

        # Add mean and median lines
        mean_mag = df["magnitude"].mean()
        median_mag = df["magnitude"].median()
        plt.axvline(mean_mag, color="r", linestyle="--", label=f"Mean: {mean_mag:.2f}")
        plt.axvline(
            median_mag, color="g", linestyle="--", label=f"Median: {median_mag:.2f}"
        )
        plt.legend()

        plt.savefig(
            f"{viz_dir}/magnitude_distribution.png", dpi=300, bbox_inches="tight"
        )
        plt.close()
        log_debug("Completed magnitude histogram")

        # 2. Create enhanced time series of earthquake counts
        log_debug("Creating time series chart")
        df["date"] = df["dt"].dt.date
        daily_counts = df.groupby("date").size().reset_index(name="count")

        plt.figure(figsize=(12, 6))
        plt.plot(
            daily_counts["date"],
            daily_counts["count"],
            marker="o",
            linestyle="-",
            linewidth=2,
            markersize=8,
            color="#1f77b4",
        )

        # Add 3-day moving average
        if len(daily_counts) >= 3:
            daily_counts["moving_avg"] = daily_counts["count"].rolling(window=3).mean()
            plt.plot(
                daily_counts["date"],
                daily_counts["moving_avg"],
                color="red",
                linestyle="--",
                linewidth=2,
                label="3-day Moving Average",
            )
            plt.legend()

        plt.title("Daily Earthquake Counts", fontsize=16)
        plt.xlabel("Date", fontsize=14)
        plt.ylabel("Number of Earthquakes", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle="--")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Add annotations for days with highest counts
        if not daily_counts.empty:
            max_count_idx = daily_counts["count"].idxmax()
            max_date = daily_counts.loc[max_count_idx, "date"]
            max_count = daily_counts.loc[max_count_idx, "count"]
            plt.annotate(
                f"Peak: {max_count}",
                xy=(max_date, max_count),
                xytext=(0, 20),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color="black"),
                ha="center",
            )

        plt.savefig(f"{viz_dir}/daily_counts.png", dpi=300, bbox_inches="tight")
        plt.close()
        log_debug("Completed time series chart")

        # 3. Create enhanced depth vs magnitude scatter plot
        log_debug("Creating depth vs magnitude plot")
        plt.figure(figsize=(10, 6))

        # Create a colormap based on depth
        scatter = plt.scatter(
            df["depth"],
            df["magnitude"],
            alpha=0.7,
            c=df["depth"],
            s=df["magnitude"] * 20,  # Size based on magnitude
            cmap="viridis",
        )

        cbar = plt.colorbar(scatter, label="Depth (km)")
        plt.title("Earthquake Depth vs Magnitude", fontsize=16)
        plt.xlabel("Depth (km)", fontsize=14)
        plt.ylabel("Magnitude", fontsize=14)
        plt.grid(True, alpha=0.3, linestyle="--")

        # Add regression line
        try:
            from scipy import stats

            if len(df) > 1:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    df["depth"], df["magnitude"]
                )
                x_line = np.array([df["depth"].min(), df["depth"].max()])
                y_line = slope * x_line + intercept
                plt.plot(
                    x_line,
                    y_line,
                    color="red",
                    linestyle="--",
                    label=f"Regression (r²={r_value**2:.2f})",
                )
                plt.legend()
        except ImportError:
            log_debug("scipy not available for regression line - skipping")

        plt.savefig(f"{viz_dir}/depth_vs_magnitude.png", dpi=300, bbox_inches="tight")
        plt.close()
        log_debug("Completed depth vs magnitude plot")

        # 4. Create an enhanced interactive map
        log_debug("Creating interactive map")
        # Start map centered at median location
        center_lat = df["latitude"].median()
        center_lon = df["longitude"].median()
        m = folium.Map(
            location=[center_lat, center_lon], zoom_start=3, tiles="CartoDB positron"
        )

        # Add measure tool
        m.add_child(MeasureControl())

        # Add a heatmap layer
        heat_data = [
            [row["latitude"], row["longitude"], row["magnitude"]]
            for _, row in df.iterrows()
        ]
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            gradient={0.4: "blue", 0.65: "lime", 0.9: "orange", 1: "red"},
        ).add_to(m)

        # Create a separate layer for markers
        marker_cluster = MarkerCluster(name="Earthquakes").add_to(m)

        # Add markers for each earthquake
        for _, row in df.iterrows():
            popup_text = f"""
            <b>Location:</b> {row['place']}<br>
            <b>Region:</b> {row['region']}<br>
            <b>Date:</b> {row['dt']}<br>
            <b>Magnitude:</b> {row['magnitude']}<br>
            <b>Depth:</b> {row['depth']} km
            """

            # Determine marker color and size based on magnitude
            if row["magnitude"] < 2.0:
                color = "green"
            elif row["magnitude"] < 4.0:
                color = "orange"
            else:
                color = "red"

            # Create custom icon with size based on magnitude
            icon = folium.Icon(color=color, icon="bolt", prefix="fa")

            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=icon,
            ).add_to(marker_cluster)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Save the map
        m.save(f"{viz_dir}/earthquake_map.html")
        log_debug("Completed interactive map")

        # 5. Create enhanced HTML dashboard
        log_debug("Creating dashboard HTML")
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Earthquake Data Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .dashboard {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .dashboard-header {{ text-align: center; margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
                .viz-row {{ display: flex; flex-wrap: wrap; justify-content: space-between; margin-bottom: 30px; }}
                .viz-item {{ width: 48%; margin-bottom: 20px; background-color: white; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.05); }}
                .viz-item img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                .viz-item iframe {{ width: 100%; height: 600px; border: 1px solid #ddd; }}
                .full-width {{ width: 100%; }}
                h1, h2 {{ color: #2c3e50; }}
                h2 {{ padding: 10px; background-color: #f9f9f9; margin-top: 0; }}
                .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="dashboard-header">
                    <h1>Earthquake Data Dashboard</h1>
                    <p class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="viz-row">
                    <div class="viz-item">
                        <h2>Magnitude Distribution</h2>
                        <img src="magnitude_distribution.png" alt="Magnitude Distribution">
                    </div>
                    <div class="viz-item">
                        <h2>Daily Earthquake Counts</h2>
                        <img src="daily_counts.png" alt="Daily Earthquake Counts">
                    </div>
                </div>
                
                <div class="viz-row">
                    <div class="viz-item">
                        <h2>Depth vs Magnitude</h2>
                        <img src="depth_vs_magnitude.png" alt="Depth vs Magnitude">
                    </div>
                    <div class="viz-item">
                        <h2>Summary Statistics</h2>
                        <table>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                            <tr>
                                <td>Total Earthquakes</td>
                                <td>{len(df)}</td>
                            </tr>
                            <tr>
                                <td>Average Magnitude</td>
                                <td>{df['magnitude'].mean():.2f}</td>
                            </tr>
                            <tr>
                                <td>Max Magnitude</td>
                                <td>{df['magnitude'].max():.2f}</td>
                            </tr>
                            <tr>
                                <td>Min Magnitude</td>
                                <td>{df['magnitude'].min():.2f}</td>
                            </tr>
                            <tr>
                                <td>Average Depth</td>
                                <td>{df['depth'].mean():.2f} km</td>
                            </tr>
                            <tr>
                                <td>Date Range</td>
                                <td>{df['dt'].min().strftime('%Y-%m-%d')} to {df['dt'].max().strftime('%Y-%m-%d')}</td>
                            </tr>
                            <tr>
                                <td>Regions with Most Activity</td>
                                <td>{', '.join(df['region'].value_counts().head(3).index.tolist())}</td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <div class="viz-row">
                    <div class="viz-item full-width">
                        <h2>Interactive Earthquake Map</h2>
                        <iframe src="earthquake_map.html"></iframe>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        with open(f"{viz_dir}/dashboard.html", "w") as f:
            f.write(dashboard_html)
        log_debug("Dashboard HTML created successfully")

        # Listing all files in visualization directory
        file_list = os.listdir(viz_dir)
        log_debug(f"Files in visualization directory: {file_list}")

        return f"{viz_dir}/dashboard.html"

    except Exception as e:
        import traceback

        error_message = (
            f"Error in visualization task: {str(e)}\n{traceback.format_exc()}"
        )
        log_debug(error_message)

        # Write error to file
        with open(f"{viz_dir}/error.html", "w") as f:
            f.write(
                f"<html><body><h1>Error in Visualization Task</h1><pre>{error_message}</pre></body></html>"
            )

        return f"{viz_dir}/error.html"


visualization_task = PythonOperator(
    task_id="generate_visualizations",
    python_callable=generate_earthquake_visualizations,
    dag=dag,
)

# Set up task dependencies
run_migrations >> extract_task >> load_task >> transform_task >> visualization_task
