# Earthquake ETL Pipeline

An ETL (Extract, Transform, Load) pipeline for collecting earthquake data from the USGS API and storing it in a PostgreSQL database. This project demonstrates a production-ready data pipeline using modern Python tools and containerization.

## Features

- **Data Extraction**: Fetches earthquake data from the USGS Earthquake API
- **Data Transformation**: Processes and prepares earthquake data for storage
- **Data Loading**: Stores processed data in PostgreSQL database
- **Database Migrations**: Uses Alembic for schema versioning and migration
- **Containerization**: Dockerized setup for consistent deployment
- **Dependency Management**: Uses Poetry for Python dependency management

## Prerequisites

- Docker and Docker Compose
- Poetry (for local development)
- Python 3.12+
- Git

## Quick Start with Docker

The easiest way to run the pipeline is with Docker:

```bash
# Clone the repository
git clone
cd analyst-builder-pipelines

# Start the pipeline
docker-compose up -d

# Check the logs
docker-compose logs -f
```

This will:

1. Start a PostgreSQL database
2. Run database migrations
3. Fetch earthquake data from USGS
4. Load the data into PostgreSQL

## Local Development Setup

To set up the project for local development:

```bash
# Clone the repository
git clone
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
```

## Project Structure

```
analyst-builder-pipelines/
├── alembic/              # Database migration scripts
│   ├── versions/         # Migration version files
│   └── env.py            # Alembic environment config
├── app/                  # Application code
│   ├── etl/              # ETL process modules
│   │   ├── process_earthquake_data.py  # Data extraction and transformation
│   │   └── load_data.py  # Data loading to PostgreSQL
│   └── models.py         # SQLAlchemy database models
├── data/                 # Directory for processed data files (not in Git)
├── docker/               # Docker configuration
│   ├── Dockerfile        # Application Dockerfile
│   └── entrypoint.sh     # Docker entry point script
├── .env                  # Environment variables (not in Git)
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker Compose configuration
├── pyproject.toml        # Poetry project definition
└── README.md             # This file
```

## Configuration

Configuration is managed through environment variables:

| Variable | Description              | Default       |
| -------- | ------------------------ | ------------- |
| DB_HOST  | PostgreSQL host          | localhost     |
| DB_PORT  | PostgreSQL port          | 5432          |
| DB_NAME  | PostgreSQL database name | earthquake_db |
| DB_USER  | PostgreSQL username      | postgres      |
| DB_PASS  | PostgreSQL password      | postgres      |

## ETL Pipeline Details

The ETL pipeline consists of the following steps:

1. **Extract**: Fetch earthquake data from the USGS API for the last 15 days
2. **Transform**: Process the JSON response and extract relevant earthquake information
3. **Load**: Store the processed data in a PostgreSQL database

The pipeline runs in these sequential steps:

```bash
# Apply database migrations
alembic upgrade head

# Process earthquake data
python -m app.etl.process_earthquake_data

# Load data to database
python -m app.etl.load_data
```

## Database Schema

The database uses a simple schema to store earthquake data:

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

## Data Files

Data files (\*.csv) are not tracked in this repository. The ETL pipeline will
generate these files in the `data/` directory. These files are excluded from
version control to:

1. Avoid storing large files in Git
2. Prevent accidentally committing sensitive data
3. Keep the repository clean

The data directory structure is preserved with `.gitkeep` files.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

- Check if the PostgreSQL container is running: `docker-compose ps`
- Verify the environment variables match your database configuration
- Check the PostgreSQL logs: `docker-compose logs postgres`

### ETL Process Failures

If the ETL process fails:

- Check the application logs: `docker-compose logs etl_app`
- Ensure you have internet connectivity to access the USGS API
- Verify the database migrations have been applied

## Maintenance

### Updating Dependencies

```bash
# Update all dependencies
poetry update

# Update a specific dependency
poetry update package-name
```

### Running the Pipeline Manually

```bash
# In Docker
docker-compose run --rm etl_app python -m app.etl.process_earthquake_data
docker-compose run --rm etl_app python -m app.etl.load_data

# Locally with Poetry
poetry run python -m app.etl.process_earthquake_data
poetry run python -m app.etl.load_data
```
