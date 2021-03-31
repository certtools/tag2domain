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

if [ -z "$TAG2DOMAIN_INTXN_TABLE_NAME" ]; then
    error_exit "TAG2DOMAIN_INTXN_TABLE_NAME is not set"
fi

if [ -z "$TAG2DOMAIN_ENTITY_TABLE" ]; then
    error_exit "TAG2DOMAIN_ENTITY_TABLE is not set"
fi

if [ -z "$TAG2DOMAIN_ENTITY_ID_COLUMN" ]; then
    error_exit "TAG2DOMAIN_ENTITY_ID_COLUMN is not set"
fi

if [ -z "$TAG2DOMAIN_ENTITY_NAME_COLUMN" ]; then
    error_exit "TAG2DOMAIN_ENTITY_NAME_COLUMN is not set"
fi

if [ -z "$TAG2DOMAIN_TAG_TYPE" ]; then
    error_exit "TAG2DOMAIN_TAG_TYPE is not set"
fi

if [[ $TAG2DOMAIN_TAG_TYPE == *"."* ]]; then
  error_exit "<TAG TYPE> can not contain a ."
fi

function run_psql_script {
  psql \
    -v ON_ERROR_STOP=1 \
    -v t2d_schema="$TAG2DOMAIN_SCHEMA" \
    -v t2d_intxn_table_name="$TAG2DOMAIN_INTXN_TABLE_NAME" \
    -v t2d_entity_table="$TAG2DOMAIN_ENTITY_TABLE" \
    -v t2d_entity_id_column="$TAG2DOMAIN_ENTITY_ID_COLUMN" \
    -v t2d_entity_name_column="$TAG2DOMAIN_ENTITY_NAME_COLUMN" \
    -v t2d_tag_type="$TAG2DOMAIN_TAG_TYPE" \
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

run_psql_script "create_glue.sql"