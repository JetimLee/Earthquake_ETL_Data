#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Execute the provided command
exec "$@"
EOF

# Make it executable
chmod +x docker/entrypoint.sh