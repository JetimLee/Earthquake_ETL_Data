# Earthquake Data Pipeline

A comprehensive data pipeline for processing, analyzing, and visualizing earthquake data using Apache Airflow and PostgreSQL. This project extracts earthquake data from the USGS API, transforms it, and loads it into a PostgreSQL database for analysis and visualization.

## Features

- **Data Extraction**: Fetches earthquake data from the USGS Earthquake API
- **Data Transformation**: Processes and prepares earthquake data for storage and analysis
- **Data Loading**: Stores processed data in PostgreSQL database
- **Workflow Orchestration**: Uses Apache Airflow to manage the ETL workflow (optional)
- **Data Visualization**: Serves generated visualizations through a web server
- **Database Migrations**: Uses Alembic for schema versioning and migration
- **Containerization**: Dockerized setup for consistent deployment
- **Dependency Management**: Uses Poetry for Python dependency management

## Requirements

- Docker and Docker Compose (v2 or later)
- Git
- Poetry (for local development)
- Python 3.12+
- `.env` file with configuration (see below)

## Quick Start

### Option 1: Run with Airflow (Recommended)

```bash
# Start the Airflow services
docker-compose -f docker-compose-airflow.yml up -d

# Wait for services to initialize
# Access Airflow web UI at http://localhost:8080
# Default credentials: admin/admin (configurable in .env)
```

### Option 2: Run Standalone ETL

```bash
# Start the standalone ETL process
docker-compose up -d

# This will:
# 1. Initialize the database
# 2. Process earthquake data from USGS API
# 3. Load data into PostgreSQL
# 4. Transform the data
```

### Option 3: Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd analyst-builder-pipelines

# Install dependencies with Poetry
poetry install

# Set up environment variables (copy from example)
cp .env.example .env
# Edit .env with your configuration

# Run PostgreSQL locally or with Docker
docker-compose up -d postgres

# Apply database migrations
poetry run python -m alembic upgrade head

# Run the ETL process
poetry run python -m app.etl.process_earthquake_data
poetry run python -m app.etl.load_data
poetry run python -m app.etl.transform_data
```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```
# Database Configuration
DB_HOST=localhost     # Use 'postgres' for Docker setups
DB_NAME=earthquake_db
DB_USER=postgres
DB_PASS=postgres
DB_PORT=5432

# Airflow Configuration (for Airflow setup only)
AIRFLOW_USER=admin
AIRFLOW_PASS=admin
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASS=airflow

# Processing Configuration
PROCESS_DAYS=15  # Number of days of earthquake data to process
```

An `.env.example` file is included in the repository that you can copy and modify.

## Project Structure

```
earthquake-data-pipeline/
├── alembic/                  # Database migration scripts
│   ├── versions/             # Migration version files
│   └── env.py                # Alembic environment config
├── alembic.ini               # Alembic configuration
├── app/                      # ETL application code
│   ├── etl/                  # ETL processing scripts
│   │   ├── process_earthquake_data.py  # Data extraction from USGS API
│   │   ├── load_data.py      # Data loading to PostgreSQL
│   │   └── transform_data.py # Data transformation logic
│   └── models.py             # SQLAlchemy database models
├── dags/                     # Airflow DAG definitions
├── data/                     # Data storage (not in Git)
│   └── visualizations/       # Generated visualizations
├── docker/                   # Docker configuration
│   ├── Dockerfile            # ETL application Dockerfile
│   └── Dockerfile.airflow    # Airflow Dockerfile
├── init-multiple-dbs.sh      # Database initialization script
├── logs/                     # Airflow logs
├── plugins/                  # Airflow plugins
├── docker-compose.yml        # Standalone ETL Docker Compose
├── docker-compose-airflow.yml # Airflow Docker Compose
├── pyproject.toml            # Poetry project definition
├── .env                      # Environment variables (not in Git)
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Accessing Services

- **Airflow Web UI**: http://localhost:8080
- **Visualization Server**: http://localhost:8090
- **PostgreSQL Database**: localhost:5432

## Data Pipeline Process

The ETL pipeline consists of the following steps:

1. **Extract**: Fetch earthquake data from the USGS API for the last 15 days (configurable)
2. **Transform**: Process the JSON response and extract relevant earthquake information
3. **Load**: Store the processed data in a PostgreSQL database
4. **Analyze**: Create aggregations and prepared views
5. **Visualize**: Generate visualizations available through the viz-server

The pipeline runs in these sequential steps:

```bash
# Apply database migrations
alembic upgrade head

# Process earthquake data (extract from USGS API)
python -m app.etl.process_earthquake_data

# Load data to database
python -m app.etl.load_data

# Transform data for analysis
python -m app.etl.transform_data
```

## Database Schema

The database uses the following schema to store earthquake data:

| Column    | Type       | Description                 |
| --------- | ---------- | --------------------------- |
| id        | Integer    | Primary key                 |
| time      | BigInteger | Timestamp of the earthquake |
| place     | String     | Location description        |
| magnitude | Float      | Earthquake magnitude        |
| longitude | Float      | Longitude coordinate        |
| latitude  | Float      | Latitude coordinate         |
| depth     | Float      | Depth in kilometers         |
| file_name | String     | Source file name            |

## Development Workflow

### Adding New Dependencies

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name
```

### Making Database Schema Changes

1. Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "description of changes"
```

2. Apply the migration:

```bash
poetry run alembic upgrade head
```

### Creating or Modifying Airflow DAGs

Add or modify DAG files in the `dags/` directory. The Airflow scheduler will automatically detect and load these changes.

### Customization

- Modify the number of days to process by changing the `PROCESS_DAYS` environment variable
- Add custom Airflow DAGs in the `dags` directory
- Extend the ETL process by modifying the Python scripts in `app/etl/`

## Troubleshooting

### Common Issues

- **Database Connection Failures**: Ensure PostgreSQL is healthy with `docker ps` and check logs with `docker logs earthquake_db`
- **Airflow Initialization Errors**: Check the airflow-init logs with `docker logs analyst_builder_pipelines-airflow-init-1`
- **Version Warning**: The warning about obsolete `version` attribute can be ignored or you can remove the `version` key from Docker Compose files

### Restarting Services

```bash
# Restart Airflow services
docker-compose -f docker-compose-airflow.yml down
docker-compose -f docker-compose-airflow.yml up -d

# Restart standalone ETL
docker-compose down
docker-compose up -d
```

## Development

To make changes to the pipeline:

1. Modify code in the `app` directory
2. For database schema changes, create a new Alembic migration:
   ```bash
   docker exec -it earthquake_etl alembic revision --autogenerate -m "description"
   ```
3. Rebuild and restart containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
