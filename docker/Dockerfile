FROM python:3.12-slim

WORKDIR /app

# Install required system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Configure Poetry to NOT create virtual environments
RUN poetry config virtualenvs.create false

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating a virtual environment and without installing the root project
RUN poetry install --no-interaction --no-ansi --without dev --no-root

# Copy the application code
COPY . .

# Set Python path to include the current directory
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Make entrypoint executable
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "app.etl.process_earthquake_data"]