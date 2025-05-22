#!/bin/bash

set -e
set -u

function create_user_and_database() {
    local database=$1
    local user=$2
    local password=$3
    
    echo "Processing database '$database' for user '$user'"
    
    # Check if database already exists
    if psql -lqt | cut -d \| -f 1 | grep -qw $database; then
        echo "Database '$database' already exists, skipping database creation"
    else
        echo "Creating database '$database'"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
            CREATE DATABASE $database;
EOSQL
    fi
    
    # Check if user already exists (except for postgres which always exists)
    if [ "$user" != "postgres" ]; then
        if psql -t -c '\du' | cut -d \| -f 1 | grep -qw $user; then
            echo "User '$user' already exists, skipping user creation"
        else
            echo "Creating user '$user'"
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
                CREATE USER $user WITH PASSWORD '$password';
EOSQL
        fi
    else
        echo "User 'postgres' already exists, skipping user creation"
    fi
    
    # Grant privileges (always do this to ensure proper permissions)
    echo "Granting privileges on '$database' to '$user'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
EOSQL
    
    # If user is not postgres, also grant privileges to postgres
    if [ "$user" != "postgres" ]; then
        echo "Granting privileges on '$database' to 'postgres'"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
            GRANT ALL PRIVILEGES ON DATABASE $database TO postgres;
EOSQL
    fi
}

# Create the airflow database and user
if [ -n "$AIRFLOW_DB_USER" ] && [ -n "$AIRFLOW_DB_PASS" ]; then
    echo "Setting up Airflow database and user"
    create_user_and_database "airflow" "$AIRFLOW_DB_USER" "$AIRFLOW_DB_PASS"
fi

# Create other databases from POSTGRES_MULTIPLE_DATABASES if specified
if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Setting up additional databases: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        # Skip airflow if it was already created
        if [ "$db" != "airflow" ] || [ -z "$AIRFLOW_DB_USER" ]; then
            # Skip the default database which is created automatically
            if [ "$db" != "$POSTGRES_DB" ]; then
                create_user_and_database $db "$POSTGRES_USER" "$POSTGRES_PASSWORD"
            else
                echo "Database '$POSTGRES_DB' is the default database, skipping creation"
                # Still grant privileges to ensure permissions are correct
                echo "Ensuring privileges on '$POSTGRES_DB'"
                psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
                    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOSQL
            fi
        fi
    done
    echo "Database setup completed"
fi