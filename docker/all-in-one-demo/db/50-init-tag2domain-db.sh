#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIR"

function run_psql_script {
  echo "RUNNING PSQL SCRIPT $(pwd)/$1"
  psql \
    -v ON_ERROR_STOP=1 \
    -v t2d_schema="$TAG2DOMAIN_SCHEMA" \
    -v t2d_entity_table="$TAG2DOMAIN_ENTITY_TABLE" \
    -v t2d_entity_id_column="$TAG2DOMAIN_ENTITY_ID_COLUMN" \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    -f "$1"
}

run_psql_script all-in-one-demo-sql/mock_registry_schema.sql
run_psql_script all-in-one-demo-sql/mock_registry_data.sql
run_psql_script all-in-one-demo-sql/intersections.sql
run_psql_script all-in-one-demo-sql/tag2domain_glue_tables.sql
run_psql_script all-in-one-demo-sql/data.sql