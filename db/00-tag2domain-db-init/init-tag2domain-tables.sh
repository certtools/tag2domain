#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIR"

function error_exit {
    >&2 echo "ERROR: $1"
    exit 1
}

if [ -z "$POSTGRES_USER" ]; then
    error_exit "POSTGRES_USER is not set"
fi

if [ -z "$POSTGRES_DB" ]; then
    error_exit "POSTGRES_DB is not set"
fi

if [ -z "$TAG2DOMAIN_SCHEMA" ]; then
    error_exit "TAG2DOMAIN_SCHEMA is not set"
fi

function run_psql_script {
  psql \
    -v ON_ERROR_STOP=1 \
    -v t2d_schema="$TAG2DOMAIN_SCHEMA" \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    -f "$1"
}

if [ -n "$POSTGRES_HOST" ]; then
  export PGHOST="$POSTGRES_HOST"
fi

if [ -n "$POSTGRES_PORT" ]; then
  export PGPORT="$POSTGRES_PORT"
fi

if [ -n "$POSTGRES_PASSWORD_FILE" ]; then
  export PGPASSFILE="$POSTGRES_PASSWORD_FILE"
fi

for file in $(find . -mindepth 2 -maxdepth 2 -name "*.sql" | sort); do
  run_psql_script $file
done
